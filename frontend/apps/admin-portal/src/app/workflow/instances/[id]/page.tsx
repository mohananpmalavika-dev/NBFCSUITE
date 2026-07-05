'use client'

import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useParams, useRouter } from 'next/navigation'
import Link from 'next/link'
import { ArrowLeft, GitBranch, CheckCircle, XCircle, Clock, AlertCircle } from 'lucide-react'
import { DashboardLayout } from '@/components/layout/dashboard-layout'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table'
import { Skeleton } from '@/components/ui/skeleton'
import { workflowService } from '@/services/workflow.service'
import { formatDate, formatDateTime, getStatusColor } from '@/lib/utils'
import { useToast } from '@/hooks/use-toast'
import type { WorkflowTask } from '@/types'

export default function WorkflowInstanceDetailPage() {
  const params = useParams()
  const router = useRouter()
  const queryClient = useQueryClient()
  const { toast } = useToast()
  const instanceId = params.id as string

  const [cancelReason, setCancelReason] = useState('')
  const [showCancelModal, setShowCancelModal] = useState(false)

  const { data: instance, isLoading } = useQuery({
    queryKey: ['workflow-instance', instanceId],
    queryFn: () => workflowService.getInstance(instanceId),
  })

  const { data: tasksData } = useQuery({
    queryKey: ['workflow-tasks', instanceId],
    queryFn: () => workflowService.getTasks({ instance_id: instanceId, page_size: 100 }),
  })

  const cancelMutation = useMutation({
    mutationFn: (reason: string) => workflowService.cancelInstance(instanceId, reason),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['workflow-instance', instanceId] })
      queryClient.invalidateQueries({ queryKey: ['workflow-instances'] })
      toast({
        title: 'Instance cancelled',
        description: 'Workflow instance has been cancelled',
      })
      setShowCancelModal(false)
      setCancelReason('')
    },
    onError: () => {
      toast({
        title: 'Error',
        description: 'Failed to cancel workflow instance',
        variant: 'destructive',
      })
    },
  })

  const handleCancel = () => {
    if (!cancelReason.trim()) {
      toast({
        title: 'Reason required',
        description: 'Please provide a reason for cancellation',
        variant: 'destructive',
      })
      return
    }
    cancelMutation.mutate(cancelReason)
  }

  if (isLoading) {
    return (
      <DashboardLayout>
        <div className="space-y-6">
          <Skeleton className="h-8 w-64" />
          <Skeleton className="h-48 w-full" />
        </div>
      </DashboardLayout>
    )
  }

  if (!instance?.data) {
    return (
      <DashboardLayout>
        <div className="text-center py-12">
          <AlertCircle className="h-12 w-12 mx-auto text-gray-400 mb-4" />
          <p className="text-lg text-gray-600">Workflow instance not found</p>
          <Link href="/workflow/instances">
            <Button className="mt-4">Back to Instances</Button>
          </Link>
        </div>
      </DashboardLayout>
    )
  }

  const instanceData = instance.data
  const tasks = tasksData?.data?.items || []

  return (
    <DashboardLayout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <Link href="/workflow/instances">
              <Button variant="ghost" size="icon">
                <ArrowLeft className="h-5 w-5" />
              </Button>
            </Link>
            <div>
              <h1 className="text-3xl font-bold text-gray-900">{instanceData.instance_number}</h1>
              <p className="text-gray-600 mt-1">{instanceData.template_name}</p>
            </div>
          </div>
          <div className="flex gap-3">
            {['pending', 'in_progress'].includes(instanceData.instance_status) && (
              <Button
                variant="destructive"
                onClick={() => setShowCancelModal(true)}
              >
                <XCircle className="h-4 w-4 mr-2" />
                Cancel Instance
              </Button>
            )}
          </div>
        </div>

        {/* Instance Details */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
          <Card>
            <CardHeader>
              <CardTitle className="text-sm font-medium text-gray-600">Status</CardTitle>
            </CardHeader>
            <CardContent>
              <Badge className={getStatusColor(instanceData.instance_status)}>
                {instanceData.instance_status}
              </Badge>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="text-sm font-medium text-gray-600">Current Step</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="font-semibold">
                {instanceData.current_step || 'Not started'}
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="text-sm font-medium text-gray-600">Started At</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="font-semibold">{formatDateTime(instanceData.started_at)}</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="text-sm font-medium text-gray-600">Completed At</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="font-semibold">
                {instanceData.completed_at 
                  ? formatDateTime(instanceData.completed_at)
                  : 'In progress'}
              </p>
            </CardContent>
          </Card>
        </div>

        {/* Tabs */}
        <Tabs defaultValue="tasks">
          <TabsList>
            <TabsTrigger value="tasks">Tasks ({tasks.length})</TabsTrigger>
            <TabsTrigger value="details">Instance Details</TabsTrigger>
            <TabsTrigger value="timeline">Timeline</TabsTrigger>
          </TabsList>

          {/* Tasks Tab */}
          <TabsContent value="tasks">
            <Card>
              <CardContent className="pt-6">
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Task Name</TableHead>
                      <TableHead>Task Type</TableHead>
                      <TableHead>Assigned To</TableHead>
                      <TableHead>Status</TableHead>
                      <TableHead>Due Date</TableHead>
                      <TableHead>Completed At</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {tasks.length > 0 ? (
                      tasks.map((task: WorkflowTask) => (
                        <TableRow key={task.id}>
                          <TableCell>
                            <Link 
                              href={`/workflow/tasks`}
                              className="font-medium text-blue-600 hover:underline"
                            >
                              {task.task_name}
                            </Link>
                          </TableCell>
                          <TableCell>
                            <Badge variant="outline">{task.task_type}</Badge>
                          </TableCell>
                          <TableCell>
                            {task.assigned_to || task.assigned_to_role || 'Unassigned'}
                          </TableCell>
                          <TableCell>
                            <Badge className={getStatusColor(task.task_status)}>
                              {task.task_status}
                            </Badge>
                          </TableCell>
                          <TableCell className="text-sm text-gray-600">
                            {task.due_date ? formatDate(task.due_date) : '-'}
                          </TableCell>
                          <TableCell className="text-sm text-gray-600">
                            {task.completed_at ? formatDateTime(task.completed_at) : '-'}
                          </TableCell>
                        </TableRow>
                      ))
                    ) : (
                      <TableRow>
                        <TableCell colSpan={6} className="text-center py-8 text-gray-500">
                          <Clock className="h-12 w-12 mx-auto text-gray-400 mb-2" />
                          <p>No tasks found for this instance</p>
                        </TableCell>
                      </TableRow>
                    )}
                  </TableBody>
                </Table>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Details Tab */}
          <TabsContent value="details">
            <Card>
              <CardContent className="pt-6">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div>
                    <p className="text-sm text-gray-600 mb-1">Instance ID</p>
                    <p className="font-mono text-sm">{instanceData.id}</p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-600 mb-1">Instance Number</p>
                    <p className="font-semibold">{instanceData.instance_number}</p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-600 mb-1">Template ID</p>
                    <p className="font-mono text-sm">{instanceData.template_id}</p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-600 mb-1">Template Name</p>
                    <p className="font-semibold">{instanceData.template_name}</p>
                  </div>
                  {instanceData.entity_type && (
                    <>
                      <div>
                        <p className="text-sm text-gray-600 mb-1">Entity Type</p>
                        <Badge variant="outline">{instanceData.entity_type}</Badge>
                      </div>
                      <div>
                        <p className="text-sm text-gray-600 mb-1">Entity ID</p>
                        <p className="font-mono text-sm">{instanceData.entity_id}</p>
                      </div>
                    </>
                  )}
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Timeline Tab */}
          <TabsContent value="timeline">
            <Card>
              <CardContent className="pt-6">
                <div className="space-y-4">
                  <TimelineItem
                    icon={GitBranch}
                    title="Workflow Started"
                    timestamp={instanceData.started_at}
                    color="blue"
                  />
                  
                  {tasks
                    .filter((t: WorkflowTask) => t.completed_at)
                    .sort((a: WorkflowTask, b: WorkflowTask) => 
                      new Date(a.completed_at!).getTime() - new Date(b.completed_at!).getTime()
                    )
                    .map((task: WorkflowTask) => (
                      <TimelineItem
                        key={task.id}
                        icon={task.task_status === 'completed' ? CheckCircle : XCircle}
                        title={`${task.task_name} - ${task.task_status}`}
                        description={task.comments}
                        timestamp={task.completed_at!}
                        color={task.task_status === 'completed' ? 'green' : 'red'}
                      />
                    ))}

                  {instanceData.completed_at && (
                    <TimelineItem
                      icon={
                        instanceData.instance_status === 'completed' 
                          ? CheckCircle 
                          : XCircle
                      }
                      title={`Workflow ${instanceData.instance_status}`}
                      timestamp={instanceData.completed_at}
                      color={
                        instanceData.instance_status === 'completed' 
                          ? 'green' 
                          : 'red'
                      }
                    />
                  )}
                </div>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>

        {/* Cancel Modal */}
        {showCancelModal && (
          <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
            <Card className="w-full max-w-lg">
              <CardHeader>
                <CardTitle>Cancel Workflow Instance</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <p className="text-sm text-gray-600">
                  Are you sure you want to cancel this workflow instance? This action cannot be undone.
                </p>
                
                <div className="space-y-2">
                  <label className="text-sm font-medium">Cancellation Reason *</label>
                  <textarea
                    className="w-full min-h-[100px] rounded-md border border-input bg-background px-3 py-2 text-sm"
                    placeholder="Provide a reason for cancellation..."
                    value={cancelReason}
                    onChange={(e) => setCancelReason(e.target.value)}
                  />
                </div>

                <div className="flex gap-3 pt-4">
                  <Button
                    variant="outline"
                    className="flex-1"
                    onClick={() => {
                      setShowCancelModal(false)
                      setCancelReason('')
                    }}
                  >
                    Keep Active
                  </Button>
                  <Button
                    variant="destructive"
                    className="flex-1"
                    onClick={handleCancel}
                    disabled={cancelMutation.isPending}
                  >
                    Yes, Cancel Instance
                  </Button>
                </div>
              </CardContent>
            </Card>
          </div>
        )}
      </div>
    </DashboardLayout>
  )
}

function TimelineItem({ 
  icon: Icon, 
  title, 
  description, 
  timestamp, 
  color 
}: {
  icon: any
  title: string
  description?: string
  timestamp: string
  color: 'blue' | 'green' | 'red'
}) {
  const colors = {
    blue: 'bg-blue-100 text-blue-600',
    green: 'bg-green-100 text-green-600',
    red: 'bg-red-100 text-red-600',
  }

  return (
    <div className="flex gap-4">
      <div className={`h-10 w-10 rounded-full ${colors[color]} flex items-center justify-center flex-shrink-0`}>
        <Icon className="h-5 w-5" />
      </div>
      <div className="flex-1 pb-8 border-l-2 border-gray-200 pl-4 ml-5">
        <p className="font-semibold">{title}</p>
        {description && <p className="text-sm text-gray-600 mt-1">{description}</p>}
        <p className="text-xs text-gray-500 mt-2">{formatDateTime(timestamp)}</p>
      </div>
    </div>
  )
}
