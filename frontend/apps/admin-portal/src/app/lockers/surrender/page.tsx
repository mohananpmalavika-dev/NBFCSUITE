'use client'

import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { format } from 'date-fns'
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/components/ui/card'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Textarea } from '@/components/ui/textarea'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
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
import { Alert, AlertDescription } from '@/components/ui/alert'
import { Separator } from '@/components/ui/separator'
import { Progress } from '@/components/ui/progress'
import { toast } from 'sonner'
import {
  CheckCircle,
  Clock,
  FileText,
  DollarSign,
  Key,
  Search,
  Plus,
  Eye,
  CheckSquare,
  AlertCircle,
  Award,
  TrendingUp,
} from 'lucide-react'
import {
  surrenderService,
  SurrenderRecord,
  SurrenderReason,
  SurrenderStatus,
  SurrenderEligibility,
  FinalSettlement,
} from '@/services/locker.service'

export default function VoluntarySurrenderPage() {
  const [selectedTab, setSelectedTab] = useState('overview')
  const [eligibilityDialogOpen, setEligibilityDialogOpen] = useState(false)
  const [submitDialogOpen, setSubmitDialogOpen] = useState(false)
  const [settlementDialogOpen, setSettlementDialogOpen] = useState(false)
  const [selectedSurrender, setSelectedSurrender] = useState<SurrenderRecord | null>(null)
  const [allocationIdForCheck, setAllocationIdForCheck] = useState('')
  const [filterStatus, setFilterStatus] = useState<SurrenderStatus | 'all'>('all')

  const queryClient = useQueryClient()

  // Fetch surrender records
  const { data: surrenderRecords, isLoading } = useQuery({
    queryKey: ['surrender-records', filterStatus],
    queryFn: async () => {
      const params: any = {}
      if (filterStatus !== 'all') params.status = filterStatus
      const response = await surrenderService.listSurrenderRecords(params)
      return response.data.records || []
    },
  })

  // Fetch statistics
  const { data: statistics } = useQuery({
    queryKey: ['surrender-statistics'],
    queryFn: async () => {
      const response = await surrenderService.getStatistics()
      return response.data
    },
  })

  // Fetch pending approvals
  const { data: pendingApprovals } = useQuery({
    queryKey: ['surrender-pending-approvals'],
    queryFn: async () => {
      const response = await surrenderService.getPendingApprovals()
      return response.data.pending_approvals || []
    },
  })

  // Check eligibility mutation
  const checkEligibilityMutation = useMutation({
    mutationFn: (allocationId: string) =>
      surrenderService.checkEligibility(allocationId),
    onSuccess: () => {
      toast.success('Eligibility check completed')
    },
    onError: () => {
      toast.error('Failed to check eligibility')
    },
  })

  // Submit application mutation
  const submitApplicationMutation = useMutation({
    mutationFn: (data: any) => surrenderService.submitApplication(data),
    onSuccess: () => {
      toast.success('Surrender application submitted successfully')
      setSubmitDialogOpen(false)
      queryClient.invalidateQueries({ queryKey: ['surrender-records'] })
    },
    onError: () => {
      toast.error('Failed to submit surrender application')
    },
  })

  // Calculate settlement mutation
  const calculateSettlementMutation = useMutation({
    mutationFn: (surrenderId: string) =>
      surrenderService.calculateFinalSettlement(surrenderId),
    onSuccess: () => {
      toast.success('Settlement calculated successfully')
    },
    onError: () => {
      toast.error('Failed to calculate settlement')
    },
  })

  // Helper function to get status badge
  const getStatusBadge = (status: SurrenderStatus) => {
    const statusConfig: Record<
      SurrenderStatus,
      { label: string; variant: 'default' | 'secondary' | 'destructive' | 'outline' }
    > = {
      [SurrenderStatus.APPLICATION_SUBMITTED]: {
        label: 'Submitted',
        variant: 'secondary',
      },
      [SurrenderStatus.APPROVED]: { label: 'Approved', variant: 'default' },
      [SurrenderStatus.REJECTED]: { label: 'Rejected', variant: 'destructive' },
      [SurrenderStatus.DUES_CLEARED]: { label: 'Dues Cleared', variant: 'default' },
      [SurrenderStatus.KEYS_RETURNED]: { label: 'Keys Returned', variant: 'default' },
      [SurrenderStatus.INSPECTION_DONE]: {
        label: 'Inspection Done',
        variant: 'default',
      },
      [SurrenderStatus.REFUND_PROCESSED]: {
        label: 'Refund Processed',
        variant: 'default',
      },
      [SurrenderStatus.CERTIFICATE_ISSUED]: {
        label: 'Certificate Issued',
        variant: 'default',
      },
      [SurrenderStatus.IN_PROGRESS]: { label: 'In Progress', variant: 'secondary' },
      [SurrenderStatus.COMPLETED]: { label: 'Completed', variant: 'default' },
      [SurrenderStatus.CANCELLED]: { label: 'Cancelled', variant: 'outline' },
    }

    const config = statusConfig[status] || { label: status, variant: 'outline' }
    return <Badge variant={config.variant}>{config.label}</Badge>
  }

  // Helper function to get progress percentage
  const getProgressPercentage = (status: SurrenderStatus): number => {
    const progressMap: Record<SurrenderStatus, number> = {
      [SurrenderStatus.APPLICATION_SUBMITTED]: 10,
      [SurrenderStatus.APPROVED]: 20,
      [SurrenderStatus.REJECTED]: 0,
      [SurrenderStatus.DUES_CLEARED]: 40,
      [SurrenderStatus.KEYS_RETURNED]: 50,
      [SurrenderStatus.INSPECTION_DONE]: 70,
      [SurrenderStatus.REFUND_PROCESSED]: 85,
      [SurrenderStatus.CERTIFICATE_ISSUED]: 95,
      [SurrenderStatus.IN_PROGRESS]: 60,
      [SurrenderStatus.COMPLETED]: 100,
      [SurrenderStatus.CANCELLED]: 0,
    }
    return progressMap[status] || 0
  }

  return (
    <div className="container mx-auto py-6 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Voluntary Locker Surrender</h1>
          <p className="text-muted-foreground">
            Manage locker surrender applications and processing
          </p>
        </div>
        <div className="flex gap-2">
          <Button onClick={() => setEligibilityDialogOpen(true)} variant="outline">
            <Search className="mr-2 h-4 w-4" />
            Check Eligibility
          </Button>
          <Button onClick={() => setSubmitDialogOpen(true)}>
            <Plus className="mr-2 h-4 w-4" />
            Submit Application
          </Button>
        </div>
      </div>

      {/* Statistics Cards */}
      {statistics && (
        <div className="grid gap-4 md:grid-cols-4">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <CardTitle className="text-sm font-medium">Total Applications</CardTitle>
              <FileText className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                {statistics.total_applications || 0}
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <CardTitle className="text-sm font-medium">Pending Approval</CardTitle>
              <Clock className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                {statistics.pending_approval || 0}
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <CardTitle className="text-sm font-medium">In Progress</CardTitle>
              <TrendingUp className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{statistics.in_progress || 0}</div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <CardTitle className="text-sm font-medium">Completed</CardTitle>
              <CheckCircle className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{statistics.completed || 0}</div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Main Tabs */}
      <Tabs value={selectedTab} onValueChange={setSelectedTab}>
        <TabsList>
          <TabsTrigger value="overview">Overview</TabsTrigger>
          <TabsTrigger value="pending-approval">
            Pending Approval
            {pendingApprovals && pendingApprovals.length > 0 && (
              <Badge variant="secondary" className="ml-2">
                {pendingApprovals.length}
              </Badge>
            )}
          </TabsTrigger>
          <TabsTrigger value="all-records">All Records</TabsTrigger>
        </TabsList>

        <TabsContent value="overview" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Surrender Process Overview</CardTitle>
              <CardDescription>
                Step-by-step guide for voluntary locker surrender
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-3">
                <div className="flex gap-3">
                  <div className="flex h-8 w-8 items-center justify-center rounded-full bg-primary text-primary-foreground">
                    1
                  </div>
                  <div>
                    <p className="font-medium">Submit Application</p>
                    <p className="text-sm text-muted-foreground">
                      Customer submits surrender request with reason
                    </p>
                  </div>
                </div>
                <div className="flex gap-3">
                  <div className="flex h-8 w-8 items-center justify-center rounded-full bg-primary text-primary-foreground">
                    2
                  </div>
                  <div>
                    <p className="font-medium">Approval Process</p>
                    <p className="text-sm text-muted-foreground">
                      Branch manager reviews and approves/rejects
                    </p>
                  </div>
                </div>
                <div className="flex gap-3">
                  <div className="flex h-8 w-8 items-center justify-center rounded-full bg-primary text-primary-foreground">
                    3
                  </div>
                  <div>
                    <p className="font-medium">Clear Dues</p>
                    <p className="text-sm text-muted-foreground">
                      Outstanding rent and penalties must be paid
                    </p>
                  </div>
                </div>
                <div className="flex gap-3">
                  <div className="flex h-8 w-8 items-center justify-center rounded-full bg-primary text-primary-foreground">
                    4
                  </div>
                  <div>
                    <p className="font-medium">Return Keys</p>
                    <p className="text-sm text-muted-foreground">
                      Customer returns all keys to branch
                    </p>
                  </div>
                </div>
                <div className="flex gap-3">
                  <div className="flex h-8 w-8 items-center justify-center rounded-full bg-primary text-primary-foreground">
                    5
                  </div>
                  <div>
                    <p className="font-medium">Inspection</p>
                    <p className="text-sm text-muted-foreground">
                      Branch staff inspects locker for damage
                    </p>
                  </div>
                </div>
                <div className="flex gap-3">
                  <div className="flex h-8 w-8 items-center justify-center rounded-full bg-primary text-primary-foreground">
                    6
                  </div>
                  <div>
                    <p className="font-medium">Process Refund</p>
                    <p className="text-sm text-muted-foreground">
                      Security deposit refund (minus deductions)
                    </p>
                  </div>
                </div>
                <div className="flex gap-3">
                  <div className="flex h-8 w-8 items-center justify-center rounded-full bg-primary text-primary-foreground">
                    7
                  </div>
                  <div>
                    <p className="font-medium">Issue Certificate</p>
                    <p className="text-sm text-muted-foreground">
                      Surrender completion certificate issued
                    </p>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="pending-approval" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Applications Pending Approval</CardTitle>
              <CardDescription>Review and process surrender requests</CardDescription>
            </CardHeader>
            <CardContent>
              {pendingApprovals && pendingApprovals.length > 0 ? (
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Surrender #</TableHead>
                      <TableHead>Locker</TableHead>
                      <TableHead>Customer</TableHead>
                      <TableHead>Application Date</TableHead>
                      <TableHead>Reason</TableHead>
                      <TableHead>Actions</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {pendingApprovals.map((record: SurrenderRecord) => (
                      <TableRow key={record.id}>
                        <TableCell className="font-medium">
                          {record.surrender_number}
                        </TableCell>
                        <TableCell>{record.locker_id}</TableCell>
                        <TableCell>{record.customer_id}</TableCell>
                        <TableCell>
                          {format(new Date(record.application_date), 'PP')}
                        </TableCell>
                        <TableCell>
                          {record.surrender_reason.replace(/_/g, ' ')}
                        </TableCell>
                        <TableCell>
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => setSelectedSurrender(record)}
                          >
                            <Eye className="h-4 w-4 mr-1" />
                            Review
                          </Button>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              ) : (
                <div className="text-center py-8 text-muted-foreground">
                  No pending approvals
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="all-records" className="space-y-4">
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <div>
                  <CardTitle>All Surrender Records</CardTitle>
                  <CardDescription>Complete surrender history</CardDescription>
                </div>
                <Select
                  value={filterStatus}
                  onValueChange={(v: any) => setFilterStatus(v)}
                >
                  <SelectTrigger className="w-[200px]">
                    <SelectValue placeholder="Filter by status" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="all">All Statuses</SelectItem>
                    <SelectItem value={SurrenderStatus.APPLICATION_SUBMITTED}>
                      Submitted
                    </SelectItem>
                    <SelectItem value={SurrenderStatus.APPROVED}>Approved</SelectItem>
                    <SelectItem value={SurrenderStatus.IN_PROGRESS}>
                      In Progress
                    </SelectItem>
                    <SelectItem value={SurrenderStatus.COMPLETED}>Completed</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </CardHeader>
            <CardContent>
              {isLoading ? (
                <div className="text-center py-8">Loading...</div>
              ) : surrenderRecords && surrenderRecords.length > 0 ? (
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Surrender #</TableHead>
                      <TableHead>Locker</TableHead>
                      <TableHead>Customer</TableHead>
                      <TableHead>Reason</TableHead>
                      <TableHead>Status</TableHead>
                      <TableHead>Application Date</TableHead>
                      <TableHead>Progress</TableHead>
                      <TableHead>Actions</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {surrenderRecords.map((record: SurrenderRecord) => (
                      <TableRow key={record.id}>
                        <TableCell className="font-medium">
                          {record.surrender_number}
                        </TableCell>
                        <TableCell>{record.locker_id}</TableCell>
                        <TableCell>{record.customer_id}</TableCell>
                        <TableCell>
                          {record.surrender_reason.replace(/_/g, ' ')}
                        </TableCell>
                        <TableCell>{getStatusBadge(record.status)}</TableCell>
                        <TableCell>
                          {format(new Date(record.application_date), 'PP')}
                        </TableCell>
                        <TableCell>
                          <div className="w-24">
                            <Progress value={getProgressPercentage(record.status)} />
                          </div>
                        </TableCell>
                        <TableCell>
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => setSelectedSurrender(record)}
                          >
                            <Eye className="h-4 w-4 mr-1" />
                            View
                          </Button>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              ) : (
                <div className="text-center py-8 text-muted-foreground">
                  No surrender records found
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>

      {/* Eligibility Check Dialog */}
      <Dialog open={eligibilityDialogOpen} onOpenChange={setEligibilityDialogOpen}>
        <DialogContent className="max-w-2xl">
          <DialogHeader>
            <DialogTitle>Check Surrender Eligibility</DialogTitle>
            <DialogDescription>
              Verify if an allocation is eligible for voluntary surrender
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-4">
            <div>
              <Label>Allocation ID</Label>
              <Input
                value={allocationIdForCheck}
                onChange={(e) => setAllocationIdForCheck(e.target.value)}
                placeholder="Enter allocation ID"
              />
            </div>
            <Button
              onClick={() => {
                if (allocationIdForCheck) {
                  checkEligibilityMutation.mutate(allocationIdForCheck)
                }
              }}
              disabled={!allocationIdForCheck || checkEligibilityMutation.isPending}
            >
              Check Eligibility
            </Button>

            {checkEligibilityMutation.data && (
              <Alert>
                <AlertDescription>
                  <div className="space-y-3">
                    <div className="flex items-center gap-2">
                      {checkEligibilityMutation.data.data.is_eligible ? (
                        <CheckCircle className="h-5 w-5 text-green-600" />
                      ) : (
                        <AlertCircle className="h-5 w-5 text-red-600" />
                      )}
                      <strong>
                        {checkEligibilityMutation.data.data.is_eligible
                          ? 'Eligible for Surrender'
                          : 'Not Eligible for Surrender'}
                      </strong>
                    </div>

                    {checkEligibilityMutation.data.data.outstanding_dues > 0 && (
                      <p className="text-sm">
                        <strong>Outstanding Dues:</strong> ₹
                        {checkEligibilityMutation.data.data.outstanding_dues.toLocaleString()}
                      </p>
                    )}

                    {checkEligibilityMutation.data.data.estimated_refund_amount > 0 && (
                      <p className="text-sm">
                        <strong>Estimated Refund:</strong> ₹
                        {checkEligibilityMutation.data.data.estimated_refund_amount.toLocaleString()}
                      </p>
                    )}
                  </div>
                </AlertDescription>
              </Alert>
            )}
          </div>
        </DialogContent>
      </Dialog>

      {/* Submit Application Dialog */}
      <SubmitSurrenderDialog
        open={submitDialogOpen}
        onOpenChange={setSubmitDialogOpen}
        onSubmit={(data) => submitApplicationMutation.mutate(data)}
        isLoading={submitApplicationMutation.isPending}
      />

      {/* Surrender Details Dialog */}
      {selectedSurrender && (
        <SurrenderDetailsDialog
          surrender={selectedSurrender}
          open={!!selectedSurrender}
          onOpenChange={(open) => !open && setSelectedSurrender(null)}
          onCalculateSettlement={() =>
            calculateSettlementMutation.mutate(selectedSurrender.id)
          }
          settlementData={calculateSettlementMutation.data?.data}
        />
      )}
    </div>
  )
}

// Submit Surrender Application Dialog Component
function SubmitSurrenderDialog({
  open,
  onOpenChange,
  onSubmit,
  isLoading,
}: {
  open: boolean
  onOpenChange: (open: boolean) => void
  onSubmit: (data: any) => void
  isLoading: boolean
}) {
  const [formData, setFormData] = useState({
    allocation_id: '',
    locker_id: '',
    customer_id: '',
    branch_id: '',
    application_date: new Date().toISOString().split('T')[0],
    surrender_reason: SurrenderReason.NO_LONGER_REQUIRED,
    reason_details: '',
    requested_surrender_date: '',
  })

  const handleSubmit = () => {
    onSubmit(formData)
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-2xl">
        <DialogHeader>
          <DialogTitle>Submit Surrender Application</DialogTitle>
          <DialogDescription>
            Apply for voluntary locker surrender and closure
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div>
              <Label>Allocation ID *</Label>
              <Input
                value={formData.allocation_id}
                onChange={(e) =>
                  setFormData({ ...formData, allocation_id: e.target.value })
                }
                placeholder="Enter allocation ID"
              />
            </div>
            <div>
              <Label>Locker ID *</Label>
              <Input
                value={formData.locker_id}
                onChange={(e) => setFormData({ ...formData, locker_id: e.target.value })}
                placeholder="Enter locker ID"
              />
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <Label>Customer ID *</Label>
              <Input
                value={formData.customer_id}
                onChange={(e) =>
                  setFormData({ ...formData, customer_id: e.target.value })
                }
                placeholder="Enter customer ID"
              />
            </div>
            <div>
              <Label>Branch ID *</Label>
              <Input
                value={formData.branch_id}
                onChange={(e) => setFormData({ ...formData, branch_id: e.target.value })}
                placeholder="Enter branch ID"
              />
            </div>
          </div>

          <div>
            <Label>Surrender Reason *</Label>
            <Select
              value={formData.surrender_reason}
              onValueChange={(value) =>
                setFormData({ ...formData, surrender_reason: value as SurrenderReason })
              }
            >
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value={SurrenderReason.NO_LONGER_REQUIRED}>
                  No Longer Required
                </SelectItem>
                <SelectItem value={SurrenderReason.RELOCATION}>Relocation</SelectItem>
                <SelectItem value={SurrenderReason.FINANCIAL_CONSTRAINTS}>
                  Financial Constraints
                </SelectItem>
                <SelectItem value={SurrenderReason.SWITCHING_BANK}>
                  Switching Bank
                </SelectItem>
                <SelectItem value={SurrenderReason.DISSATISFACTION}>
                  Dissatisfaction
                </SelectItem>
                <SelectItem value={SurrenderReason.OTHER}>Other</SelectItem>
              </SelectContent>
            </Select>
          </div>

          <div>
            <Label>Reason Details *</Label>
            <Textarea
              value={formData.reason_details}
              onChange={(e) =>
                setFormData({ ...formData, reason_details: e.target.value })
              }
              rows={4}
              placeholder="Please provide detailed reason for surrender"
            />
          </div>

          <div>
            <Label>Requested Surrender Date *</Label>
            <Input
              type="date"
              value={formData.requested_surrender_date}
              onChange={(e) =>
                setFormData({ ...formData, requested_surrender_date: e.target.value })
              }
              min={new Date().toISOString().split('T')[0]}
            />
          </div>

          <Alert>
            <AlertCircle className="h-4 w-4" />
            <AlertDescription>
              Please ensure all outstanding dues are cleared before submitting the
              application. Security deposit will be refunded after inspection and approval.
            </AlertDescription>
          </Alert>

          <Button onClick={handleSubmit} disabled={isLoading} className="w-full">
            {isLoading ? 'Submitting...' : 'Submit Surrender Application'}
          </Button>
        </div>
      </DialogContent>
    </Dialog>
  )
}

// Surrender Details Dialog Component
function SurrenderDetailsDialog({
  surrender,
  open,
  onOpenChange,
  onCalculateSettlement,
  settlementData,
}: {
  surrender: SurrenderRecord
  open: boolean
  onOpenChange: (open: boolean) => void
  onCalculateSettlement: () => void
  settlementData?: FinalSettlement
}) {
  const [activeTab, setActiveTab] = useState('details')

  const processSteps = [
    {
      status: SurrenderStatus.APPLICATION_SUBMITTED,
      label: 'Application Submitted',
      icon: FileText,
      completed: true,
    },
    {
      status: SurrenderStatus.APPROVED,
      label: 'Approved',
      icon: CheckCircle,
      completed: surrender.approved,
    },
    {
      status: SurrenderStatus.DUES_CLEARED,
      label: 'Dues Cleared',
      icon: DollarSign,
      completed: surrender.dues_cleared,
    },
    {
      status: SurrenderStatus.KEYS_RETURNED,
      label: 'Keys Returned',
      icon: Key,
      completed: surrender.customer_key_returned,
    },
    {
      status: SurrenderStatus.INSPECTION_DONE,
      label: 'Inspection Done',
      icon: Search,
      completed: surrender.inspection_done,
    },
    {
      status: SurrenderStatus.REFUND_PROCESSED,
      label: 'Refund Processed',
      icon: DollarSign,
      completed: surrender.refund_processed,
    },
    {
      status: SurrenderStatus.CERTIFICATE_ISSUED,
      label: 'Certificate Issued',
      icon: Award,
      completed: surrender.certificate_issued,
    },
    {
      status: SurrenderStatus.COMPLETED,
      label: 'Completed',
      icon: CheckSquare,
      completed: surrender.status === SurrenderStatus.COMPLETED,
    },
  ]

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-4xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>Surrender Details - {surrender.surrender_number}</DialogTitle>
          <DialogDescription>
            Locker ID: {surrender.locker_id} | Status: {surrender.status}
          </DialogDescription>
        </DialogHeader>

        {/* Process Timeline */}
        <Card>
          <CardHeader>
            <CardTitle className="text-base">Surrender Process Timeline</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {processSteps.map((step, index) => (
                <div key={index} className="flex items-center gap-3">
                  <div
                    className={`flex h-8 w-8 items-center justify-center rounded-full ${
                      step.completed
                        ? 'bg-green-100 text-green-600'
                        : 'bg-gray-100 text-gray-400'
                    }`}
                  >
                    <step.icon className="h-4 w-4" />
                  </div>
                  <div className="flex-1">
                    <p
                      className={`text-sm font-medium ${
                        step.completed ? 'text-foreground' : 'text-muted-foreground'
                      }`}
                    >
                      {step.label}
                    </p>
                  </div>
                  {step.completed && (
                    <CheckCircle className="h-5 w-5 text-green-600" />
                  )}
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        <Tabs value={activeTab} onValueChange={setActiveTab}>
          <TabsList className="grid w-full grid-cols-4">
            <TabsTrigger value="details">Details</TabsTrigger>
            <TabsTrigger value="financial">Financial</TabsTrigger>
            <TabsTrigger value="inspection">Inspection</TabsTrigger>
            <TabsTrigger value="settlement">Settlement</TabsTrigger>
          </TabsList>

          <TabsContent value="details" className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <Label className="text-muted-foreground">Application Date</Label>
                <p className="font-medium">
                  {format(new Date(surrender.application_date), 'PPP')}
                </p>
              </div>
              <div>
                <Label className="text-muted-foreground">Requested Date</Label>
                <p className="font-medium">
                  {format(new Date(surrender.requested_surrender_date), 'PPP')}
                </p>
              </div>
              <div>
                <Label className="text-muted-foreground">Surrender Reason</Label>
                <p className="font-medium">
                  {surrender.surrender_reason.replace(/_/g, ' ')}
                </p>
              </div>
              <div>
                <Label className="text-muted-foreground">Status</Label>
                <div>{getStatusBadge(surrender.status)}</div>
              </div>
            </div>

            <Separator />

            <div>
              <Label className="text-muted-foreground">Reason Details</Label>
              <p className="text-sm mt-1">{surrender.reason_details}</p>
            </div>

            {surrender.approved && (
              <>
                <Separator />
                <div>
                  <h3 className="font-medium mb-2">Approval Details</h3>
                  <div className="space-y-2 text-sm">
                    <p>
                      <strong>Approved By:</strong> {surrender.approved_by}
                    </p>
                    <p>
                      <strong>Approval Date:</strong>{' '}
                      {surrender.approval_date &&
                        format(new Date(surrender.approval_date), 'PPP')}
                    </p>
                    {surrender.approval_remarks && (
                      <p>
                        <strong>Remarks:</strong> {surrender.approval_remarks}
                      </p>
                    )}
                  </div>
                </div>
              </>
            )}
          </TabsContent>

          <TabsContent value="financial" className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <Label className="text-muted-foreground">Outstanding Rent</Label>
                <p className="text-lg font-semibold">
                  ₹{surrender.outstanding_rent.toLocaleString()}
                </p>
              </div>
              <div>
                <Label className="text-muted-foreground">Outstanding Penalties</Label>
                <p className="text-lg font-semibold">
                  ₹{surrender.outstanding_penalties.toLocaleString()}
                </p>
              </div>
              <div>
                <Label className="text-muted-foreground">Outstanding Charges</Label>
                <p className="text-lg font-semibold">
                  ₹{surrender.outstanding_charges.toLocaleString()}
                </p>
              </div>
              <div>
                <Label className="text-muted-foreground">Total Outstanding</Label>
                <p className="text-lg font-semibold text-red-600">
                  ₹{surrender.total_outstanding.toLocaleString()}
                </p>
              </div>
            </div>

            <Separator />

            <div>
              <h3 className="font-medium mb-3">Security Deposit Refund</h3>
              <div className="space-y-2">
                <div className="flex justify-between">
                  <span>Security Deposit:</span>
                  <span className="font-medium">
                    ₹{surrender.security_deposit_amount.toLocaleString()}
                  </span>
                </div>
                <div className="flex justify-between text-red-600">
                  <span>Damage Deductions:</span>
                  <span className="font-medium">
                    -₹{surrender.damage_deductions.toLocaleString()}
                  </span>
                </div>
                <div className="flex justify-between text-red-600">
                  <span>Outstanding Dues Deductions:</span>
                  <span className="font-medium">
                    -₹{surrender.outstanding_dues_deductions.toLocaleString()}
                  </span>
                </div>
                <div className="flex justify-between text-red-600">
                  <span>Other Deductions:</span>
                  <span className="font-medium">
                    -₹{surrender.other_deductions.toLocaleString()}
                  </span>
                </div>
                <Separator />
                <div className="flex justify-between text-lg font-bold">
                  <span>Refundable Amount:</span>
                  <span className="text-green-600">
                    ₹{surrender.refundable_amount.toLocaleString()}
                  </span>
                </div>
              </div>
            </div>

            {surrender.refund_processed && (
              <>
                <Separator />
                <Alert>
                  <CheckCircle className="h-4 w-4" />
                  <AlertDescription>
                    <strong>Refund Processed</strong>
                    <p className="mt-1 text-sm">
                      Reference: {surrender.refund_reference_number}
                      <br />
                      Date:{' '}
                      {surrender.refund_completion_date &&
                        format(new Date(surrender.refund_completion_date), 'PPP')}
                    </p>
                  </AlertDescription>
                </Alert>
              </>
            )}
          </TabsContent>

          <TabsContent value="inspection" className="space-y-4">
            {surrender.inspection_done ? (
              <>
                <Alert>
                  <CheckCircle className="h-4 w-4" />
                  <AlertDescription>
                    Inspection completed on{' '}
                    {surrender.inspection_date &&
                      format(new Date(surrender.inspection_date), 'PPP')}
                  </AlertDescription>
                </Alert>

                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <Label className="text-muted-foreground">Inspected By</Label>
                    <p className="font-medium">{surrender.inspected_by}</p>
                  </div>
                  <div>
                    <Label className="text-muted-foreground">Locker Condition</Label>
                    <p className="font-medium">
                      {surrender.locker_cleaned ? 'Cleaned' : 'Needs Cleaning'}
                    </p>
                  </div>
                  <div>
                    <Label className="text-muted-foreground">Lock Status</Label>
                    <p className="font-medium">
                      {surrender.lock_working ? 'Working' : 'Damaged'}
                    </p>
                  </div>
                  <div>
                    <Label className="text-muted-foreground">Damage Found</Label>
                    <p className="font-medium">
                      {surrender.damage_found ? 'Yes' : 'No'}
                    </p>
                  </div>
                </div>

                {surrender.damage_found && (
                  <>
                    <Separator />
                    <Alert variant="destructive">
                      <AlertCircle className="h-4 w-4" />
                      <AlertDescription>
                        <strong>Damage Detected</strong>
                        <p className="mt-1 text-sm">
                          Type: {surrender.damage_type}
                          <br />
                          Description: {surrender.damage_description}
                          <br />
                          Repair Cost: ₹
                          {surrender.damage_repair_cost?.toLocaleString() || 0}
                        </p>
                      </AlertDescription>
                    </Alert>
                  </>
                )}
              </>
            ) : (
              <Alert>
                <Clock className="h-4 w-4" />
                <AlertDescription>Inspection pending</AlertDescription>
              </Alert>
            )}
          </TabsContent>

          <TabsContent value="settlement" className="space-y-4">
            {!settlementData && (
              <div className="text-center py-8">
                <Button onClick={onCalculateSettlement}>
                  <DollarSign className="mr-2 h-4 w-4" />
                  Calculate Final Settlement
                </Button>
              </div>
            )}

            {settlementData && (
              <div className="space-y-4">
                <Alert>
                  <CheckCircle className="h-4 w-4" />
                  <AlertDescription>Final settlement calculated</AlertDescription>
                </Alert>

                <Card>
                  <CardHeader>
                    <CardTitle className="text-base">Settlement Breakdown</CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-3">
                    {settlementData.settlement_breakdown?.map((item, index) => (
                      <div key={index} className="flex justify-between">
                        <span className="text-sm">{item.description}</span>
                        <span
                          className={`font-medium ${
                            item.type === 'credit' ? 'text-green-600' : 'text-red-600'
                          }`}
                        >
                          {item.type === 'credit' ? '+' : '-'}₹
                          {item.amount.toLocaleString()}
                        </span>
                      </div>
                    ))}

                    <Separator />

                    <div className="grid grid-cols-2 gap-4 pt-2">
                      <div className="text-center p-3 bg-green-50 rounded">
                        <p className="text-xs text-muted-foreground">
                          Payment to Customer
                        </p>
                        <p className="text-lg font-bold text-green-600">
                          ₹{settlementData.payment_due_to_customer.toLocaleString()}
                        </p>
                      </div>
                      <div className="text-center p-3 bg-red-50 rounded">
                        <p className="text-xs text-muted-foreground">Payment to Bank</p>
                        <p className="text-lg font-bold text-red-600">
                          ₹{settlementData.payment_due_to_bank.toLocaleString()}
                        </p>
                      </div>
                    </div>

                    <Separator />

                    <div className="text-center p-4 bg-primary/10 rounded">
                      <p className="text-sm text-muted-foreground mb-1">
                        Net Settlement Amount
                      </p>
                      <p className="text-2xl font-bold">
                        ₹{Math.abs(settlementData.net_settlement_amount).toLocaleString()}
                      </p>
                      <p className="text-xs text-muted-foreground mt-1">
                        {settlementData.net_settlement_amount >= 0
                          ? 'Payable to Customer'
                          : 'Payable to Bank'}
                      </p>
                    </div>
                  </CardContent>
                </Card>
              </div>
            )}
          </TabsContent>
        </Tabs>

        <Separator />

        <div className="flex justify-end gap-2">
          <Button variant="outline" onClick={() => onOpenChange(false)}>
            Close
          </Button>
        </div>
      </DialogContent>
    </Dialog>
  )
}
