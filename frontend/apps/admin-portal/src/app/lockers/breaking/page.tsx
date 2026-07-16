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
  DialogTrigger,
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
import { toast } from 'sonner'
import {
  AlertTriangle,
  CheckCircle,
  Clock,
  FileText,
  Video,
  Package,
  DollarSign,
  Eye,
  Plus,
  Search,
  Filter,
  Download,
  Shield,
  Users,
  MapPin,
} from 'lucide-react'
import {
  breakingService,
  BreakingRecord,
  BreakingReason,
  BreakingStatus,
  BreakingAuthorization,
  InventoryItem,
  type BreakingWitness,
} from '@/services/locker.service'

export default function LockerBreakingPage() {
  const [selectedTab, setSelectedTab] = useState('overview')
  const [authCheckDialogOpen, setAuthCheckDialogOpen] = useState(false)
  const [initiateDialogOpen, setInitiateDialogOpen] = useState(false)
  const [inventoryDialogOpen, setInventoryDialogOpen] = useState(false)
  const [chargesDialogOpen, setChargesDialogOpen] = useState(false)
  const [selectedBreaking, setSelectedBreaking] = useState<BreakingRecord | null>(null)
  const [allocationIdForCheck, setAllocationIdForCheck] = useState('')
  const [filterStatus, setFilterStatus] = useState<BreakingStatus | 'all'>('all')
  const [filterReason, setFilterReason] = useState<BreakingReason | 'all'>('all')

  const queryClient = useQueryClient()

  // Fetch breaking records
  const { data: breakingRecords, isLoading } = useQuery({
    queryKey: ['breaking-records', filterStatus, filterReason],
    queryFn: async () => {
      const params: any = {}
      if (filterStatus !== 'all') params.status = filterStatus
      if (filterReason !== 'all') params.reason = filterReason
      const response = await breakingService.listBreakingRecords(params)
      return response.data.records || []
    },
  })

  // Fetch statistics
  const { data: statistics } = useQuery({
    queryKey: ['breaking-statistics'],
    queryFn: async () => {
      const response = await breakingService.getStatistics()
      return response.data
    },
  })

  // Fetch pending action
  const { data: pendingAction } = useQuery({
    queryKey: ['breaking-pending-action'],
    queryFn: async () => {
      const response = await breakingService.getPendingAction()
      return response.data.pending_records || []
    },
  })

  // Check authorization mutation
  const checkAuthMutation = useMutation({
    mutationFn: (allocationId: string) =>
      breakingService.checkBreakingAuthorization(allocationId),
    onSuccess: (response) => {
      toast.success('Authorization check completed')
    },
    onError: () => {
      toast.error('Failed to check authorization')
    },
  })

  // Initiate breaking mutation
  const initiateBreakingMutation = useMutation({
    mutationFn: (data: any) => breakingService.initiateBreaking(data),
    onSuccess: () => {
      toast.success('Locker breaking initiated successfully')
      setInitiateDialogOpen(false)
      queryClient.invalidateQueries({ queryKey: ['breaking-records'] })
      queryClient.invalidateQueries({ queryKey: ['breaking-statistics'] })
    },
    onError: () => {
      toast.error('Failed to initiate breaking')
    },
  })

  // Record videography mutation
  const videographyMutation = useMutation({
    mutationFn: ({ breakingId, data }: { breakingId: string; data: any }) =>
      breakingService.recordVideography(breakingId, data),
    onSuccess: () => {
      toast.success('Videography recorded successfully')
      queryClient.invalidateQueries({ queryKey: ['breaking-records'] })
    },
    onError: () => {
      toast.error('Failed to record videography')
    },
  })

  // Prepare inventory mutation
  const inventoryMutation = useMutation({
    mutationFn: ({ breakingId, data }: { breakingId: string; data: any }) =>
      breakingService.prepareInventory(breakingId, data),
    onSuccess: () => {
      toast.success('Inventory prepared successfully')
      setInventoryDialogOpen(false)
      queryClient.invalidateQueries({ queryKey: ['breaking-records'] })
    },
    onError: () => {
      toast.error('Failed to prepare inventory')
    },
  })

  // Calculate charges mutation
  const chargesMutation = useMutation({
    mutationFn: ({ breakingId, data }: { breakingId: string; data: any }) =>
      breakingService.calculateBreakingCharges(breakingId, data),
    onSuccess: () => {
      toast.success('Breaking charges calculated successfully')
      setChargesDialogOpen(false)
      queryClient.invalidateQueries({ queryKey: ['breaking-records'] })
    },
    onError: () => {
      toast.error('Failed to calculate charges')
    },
  })

  // Complete breaking mutation
  const completeBreakingMutation = useMutation({
    mutationFn: ({ breakingId, data }: { breakingId: string; data: any }) =>
      breakingService.completeBreaking(breakingId, data),
    onSuccess: () => {
      toast.success('Locker breaking completed successfully')
      queryClient.invalidateQueries({ queryKey: ['breaking-records'] })
      queryClient.invalidateQueries({ queryKey: ['breaking-statistics'] })
    },
    onError: () => {
      toast.error('Failed to complete breaking')
    },
  })

  const getStatusBadge = (status: BreakingStatus) => {
    const statusConfig = {
      [BreakingStatus.AUTHORIZED]: { label: 'Authorized', variant: 'secondary' as const },
      [BreakingStatus.INITIATED]: { label: 'Initiated', variant: 'default' as const },
      [BreakingStatus.VIDEOGRAPHY_DONE]: { label: 'Videography Done', variant: 'default' as const },
      [BreakingStatus.INVENTORY_PREPARED]: { label: 'Inventory Prepared', variant: 'default' as const },
      [BreakingStatus.VALUATION_DONE]: { label: 'Valuation Done', variant: 'default' as const },
      [BreakingStatus.CONTENTS_STORED]: { label: 'Contents Stored', variant: 'default' as const },
      [BreakingStatus.CHARGES_CALCULATED]: { label: 'Charges Calculated', variant: 'default' as const },
      [BreakingStatus.COMPLETED]: { label: 'Completed', variant: 'success' as const },
      [BreakingStatus.CANCELLED]: { label: 'Cancelled', variant: 'destructive' as const },
    }

    const config = statusConfig[status] || { label: status, variant: 'default' as const }
    return <Badge variant={config.variant}>{config.label}</Badge>
  }

  return (
    <div className="container mx-auto p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Locker Breaking Management</h1>
          <p className="text-muted-foreground mt-1">
            Manage forced locker opening procedures and breaking processes
          </p>
        </div>
        <div className="flex gap-2">
          <Button
            variant="outline"
            onClick={() => setAuthCheckDialogOpen(true)}
          >
            <Shield className="mr-2 h-4 w-4" />
            Check Authorization
          </Button>
          <Button onClick={() => setInitiateDialogOpen(true)}>
            <Plus className="mr-2 h-4 w-4" />
            Initiate Breaking
          </Button>
        </div>
      </div>

      {/* Statistics Cards */}
      {statistics && (
        <div className="grid gap-4 md:grid-cols-4">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Total Breakings</CardTitle>
              <FileText className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{statistics.total_breakings}</div>
              <p className="text-xs text-muted-foreground">
                {statistics.completed_this_month} this month
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Pending Breakings</CardTitle>
              <Clock className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{statistics.pending_breakings}</div>
              <p className="text-xs text-muted-foreground">
                Avg. {statistics.average_days_to_complete} days to complete
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Contents in Custody</CardTitle>
              <Package className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{statistics.contents_in_custody}</div>
              <p className="text-xs text-muted-foreground">
                {statistics.unclaimed_contents} unclaimed
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Total Charges</CardTitle>
              <DollarSign className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                ₹{statistics.total_charges_collected?.toLocaleString()}
              </div>
              <p className="text-xs text-muted-foreground">Collected charges</p>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Main Content Tabs */}
      <Tabs value={selectedTab} onValueChange={setSelectedTab}>
        <TabsList>
          <TabsTrigger value="overview">Overview</TabsTrigger>
          <TabsTrigger value="pending">
            Pending Action
            {pendingAction && pendingAction.length > 0 && (
              <Badge variant="destructive" className="ml-2">
                {pendingAction.length}
              </Badge>
            )}
          </TabsTrigger>
          <TabsTrigger value="all-records">All Records</TabsTrigger>
        </TabsList>

        <TabsContent value="overview" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Breaking Process Overview</CardTitle>
              <CardDescription>
                Track the status of locker breaking procedures
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {statistics?.by_status && (
                  <div className="grid gap-4 md:grid-cols-3">
                    {Object.entries(statistics.by_status).map(([status, count]) => (
                      <div
                        key={status}
                        className="flex items-center justify-between p-4 border rounded-lg"
                      >
                        <div>
                          <p className="text-sm font-medium">{status}</p>
                          <p className="text-2xl font-bold">{count as number}</p>
                        </div>
                        {getStatusBadge(status as BreakingStatus)}
                      </div>
                    ))}
                  </div>
                )}

                <Separator />

                <div>
                  <h3 className="font-medium mb-3">Breaking by Reason</h3>
                  <div className="space-y-2">
                    {statistics?.by_reason &&
                      Object.entries(statistics.by_reason).map(([reason, count]) => (
                        <div
                          key={reason}
                          className="flex items-center justify-between p-2 hover:bg-accent rounded"
                        >
                          <span className="text-sm">{reason.replace(/_/g, ' ')}</span>
                          <Badge variant="outline">{count as number}</Badge>
                        </div>
                      ))}
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="pending" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Breaking Records Pending Action</CardTitle>
              <CardDescription>
                Breakings requiring immediate attention
              </CardDescription>
            </CardHeader>
            <CardContent>
              {pendingAction && pendingAction.length > 0 ? (
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Breaking Number</TableHead>
                      <TableHead>Locker</TableHead>
                      <TableHead>Reason</TableHead>
                      <TableHead>Status</TableHead>
                      <TableHead>Scheduled Date</TableHead>
                      <TableHead>Actions</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {pendingAction.map((record: BreakingRecord) => (
                      <TableRow key={record.id}>
                        <TableCell className="font-medium">
                          {record.breaking_number}
                        </TableCell>
                        <TableCell>{record.locker_id}</TableCell>
                        <TableCell>
                          {record.breaking_reason.replace(/_/g, ' ')}
                        </TableCell>
                        <TableCell>{getStatusBadge(record.status)}</TableCell>
                        <TableCell>
                          {format(new Date(record.breaking_scheduled_date), 'PP')}
                        </TableCell>
                        <TableCell>
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => setSelectedBreaking(record)}
                          >
                            <Eye className="h-4 w-4" />
                          </Button>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              ) : (
                <div className="text-center py-8 text-muted-foreground">
                  No pending actions
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
                  <CardTitle>All Breaking Records</CardTitle>
                  <CardDescription>Complete history of locker breakings</CardDescription>
                </div>
                <div className="flex gap-2">
                  <Select value={filterStatus} onValueChange={(v: any) => setFilterStatus(v)}>
                    <SelectTrigger className="w-[180px]">
                      <SelectValue placeholder="Filter by status" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="all">All Statuses</SelectItem>
                      <SelectItem value={BreakingStatus.AUTHORIZED}>Authorized</SelectItem>
                      <SelectItem value={BreakingStatus.INITIATED}>Initiated</SelectItem>
                      <SelectItem value={BreakingStatus.COMPLETED}>Completed</SelectItem>
                    </SelectContent>
                  </Select>

                  <Select value={filterReason} onValueChange={(v: any) => setFilterReason(v)}>
                    <SelectTrigger className="w-[180px]">
                      <SelectValue placeholder="Filter by reason" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="all">All Reasons</SelectItem>
                      <SelectItem value={BreakingReason.NON_PAYMENT}>Non-Payment</SelectItem>
                      <SelectItem value={BreakingReason.DEATH_OF_HOLDER}>Death</SelectItem>
                      <SelectItem value={BreakingReason.COURT_ORDER}>Court Order</SelectItem>
                      <SelectItem value={BreakingReason.EMERGENCY}>Emergency</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>
            </CardHeader>
            <CardContent>
              {isLoading ? (
                <div className="text-center py-8">Loading...</div>
              ) : breakingRecords && breakingRecords.length > 0 ? (
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Breaking Number</TableHead>
                      <TableHead>Locker</TableHead>
                      <TableHead>Customer</TableHead>
                      <TableHead>Reason</TableHead>
                      <TableHead>Status</TableHead>
                      <TableHead>Scheduled</TableHead>
                      <TableHead>Charges</TableHead>
                      <TableHead>Actions</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {breakingRecords.map((record: BreakingRecord) => (
                      <TableRow key={record.id}>
                        <TableCell className="font-medium">
                          {record.breaking_number}
                        </TableCell>
                        <TableCell>{record.locker_id}</TableCell>
                        <TableCell>{record.customer_id}</TableCell>
                        <TableCell>
                          {record.breaking_reason.replace(/_/g, ' ')}
                        </TableCell>
                        <TableCell>{getStatusBadge(record.status)}</TableCell>
                        <TableCell>
                          {format(new Date(record.breaking_scheduled_date), 'PP')}
                        </TableCell>
                        <TableCell>
                          {record.total_charges
                            ? `₹${record.total_charges.toLocaleString()}`
                            : '-'}
                        </TableCell>
                        <TableCell>
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => setSelectedBreaking(record)}
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
                  No breaking records found
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>

      {/* Authorization Check Dialog */}
      <Dialog open={authCheckDialogOpen} onOpenChange={setAuthCheckDialogOpen}>
        <DialogContent className="max-w-2xl">
          <DialogHeader>
            <DialogTitle>Check Breaking Authorization</DialogTitle>
            <DialogDescription>
              Verify if an allocation is authorized for locker breaking
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
                  checkAuthMutation.mutate(allocationIdForCheck)
                }
              }}
              disabled={!allocationIdForCheck || checkAuthMutation.isPending}
            >
              Check Authorization
            </Button>

            {checkAuthMutation.data && (
              <Alert>
                <AlertDescription>
                  <div className="space-y-2">
                    <p>
                      <strong>Authorized:</strong>{' '}
                      {checkAuthMutation.data.data.is_authorized ? 'Yes' : 'No'}
                    </p>
                    {checkAuthMutation.data.data.authorization_reasons && (
                      <div>
                        <strong>Reasons:</strong>
                        <ul className="list-disc list-inside">
                          {checkAuthMutation.data.data.authorization_reasons.map(
                            (reason: string, idx: number) => (
                              <li key={idx}>{reason}</li>
                            )
                          )}
                        </ul>
                      </div>
                    )}
                  </div>
                </AlertDescription>
              </Alert>
            )}
          </div>
        </DialogContent>
      </Dialog>

      {/* Initiate Breaking Dialog */}
      <InitiateBreakingDialog
        open={initiateDialogOpen}
        onOpenChange={setInitiateDialogOpen}
        onSubmit={(data) => initiateBreakingMutation.mutate(data)}
        isLoading={initiateBreakingMutation.isPending}
      />

      {/* Breaking Details Dialog */}
      {selectedBreaking && (
        <BreakingDetailsDialog
          breaking={selectedBreaking}
          open={!!selectedBreaking}
          onOpenChange={(open) => !open && setSelectedBreaking(null)}
          onVideographySubmit={(data) =>
            videographyMutation.mutate({
              breakingId: selectedBreaking.id,
              data,
            })
          }
          onInventorySubmit={(data) =>
            inventoryMutation.mutate({
              breakingId: selectedBreaking.id,
              data,
            })
          }
          onChargesSubmit={(data) =>
            chargesMutation.mutate({
              breakingId: selectedBreaking.id,
              data,
            })
          }
          onComplete={(data) =>
            completeBreakingMutation.mutate({
              breakingId: selectedBreaking.id,
              data,
            })
          }
        />
      )}
    </div>
  )
}

// Initiate Breaking Dialog Component
function InitiateBreakingDialog({
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
    breaking_reason: BreakingReason.NON_PAYMENT,
    reason_details: '',
    authorized_by_branch_manager: '',
    branch_manager_approval_date: '',
    authorized_by_regional_head: '',
    regional_head_approval_date: '',
    witness_1_name: '',
    witness_1_employee_id: '',
    witness_2_name: '',
    witness_2_employee_id: '',
    breaking_scheduled_date: '',
    police_intimation_required: false,
    legal_notice_sent: false,
  })

  const handleSubmit = () => {
    onSubmit({
      ...formData,
      witness_1: {
        name: formData.witness_1_name,
        employee_id: formData.witness_1_employee_id,
      },
      witness_2: {
        name: formData.witness_2_name,
        employee_id: formData.witness_2_employee_id,
      },
    })
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-3xl max-h-[80vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>Initiate Locker Breaking</DialogTitle>
          <DialogDescription>
            Begin the forced opening procedure for a locker
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
              />
            </div>
            <div>
              <Label>Locker ID *</Label>
              <Input
                value={formData.locker_id}
                onChange={(e) =>
                  setFormData({ ...formData, locker_id: e.target.value })
                }
              />
            </div>
          </div>

          <div>
            <Label>Breaking Reason *</Label>
            <Select
              value={formData.breaking_reason}
              onValueChange={(value) =>
                setFormData({ ...formData, breaking_reason: value as BreakingReason })
              }
            >
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value={BreakingReason.NON_PAYMENT}>Non-Payment</SelectItem>
                <SelectItem value={BreakingReason.DEATH_OF_HOLDER}>Death of Holder</SelectItem>
                <SelectItem value={BreakingReason.COURT_ORDER}>Court Order</SelectItem>
                <SelectItem value={BreakingReason.SUSPICIOUS_ACTIVITY}>
                  Suspicious Activity
                </SelectItem>
                <SelectItem value={BreakingReason.EMERGENCY}>Emergency</SelectItem>
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
              rows={3}
            />
          </div>

          <Separator />
          <h3 className="font-medium">Authorization</h3>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <Label>Branch Manager Name *</Label>
              <Input
                value={formData.authorized_by_branch_manager}
                onChange={(e) =>
                  setFormData({
                    ...formData,
                    authorized_by_branch_manager: e.target.value,
                  })
                }
              />
            </div>
            <div>
              <Label>BM Approval Date *</Label>
              <Input
                type="date"
                value={formData.branch_manager_approval_date}
                onChange={(e) =>
                  setFormData({
                    ...formData,
                    branch_manager_approval_date: e.target.value,
                  })
                }
              />
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <Label>Regional Head Name *</Label>
              <Input
                value={formData.authorized_by_regional_head}
                onChange={(e) =>
                  setFormData({
                    ...formData,
                    authorized_by_regional_head: e.target.value,
                  })
                }
              />
            </div>
            <div>
              <Label>RH Approval Date *</Label>
              <Input
                type="date"
                value={formData.regional_head_approval_date}
                onChange={(e) =>
                  setFormData({
                    ...formData,
                    regional_head_approval_date: e.target.value,
                  })
                }
              />
            </div>
          </div>

          <Separator />
          <h3 className="font-medium">Witnesses (Minimum 2 Required)</h3>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <Label>Witness 1 Name *</Label>
              <Input
                value={formData.witness_1_name}
                onChange={(e) =>
                  setFormData({ ...formData, witness_1_name: e.target.value })
                }
              />
            </div>
            <div>
              <Label>Witness 1 Employee ID *</Label>
              <Input
                value={formData.witness_1_employee_id}
                onChange={(e) =>
                  setFormData({ ...formData, witness_1_employee_id: e.target.value })
                }
              />
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <Label>Witness 2 Name *</Label>
              <Input
                value={formData.witness_2_name}
                onChange={(e) =>
                  setFormData({ ...formData, witness_2_name: e.target.value })
                }
              />
            </div>
            <div>
              <Label>Witness 2 Employee ID *</Label>
              <Input
                value={formData.witness_2_employee_id}
                onChange={(e) =>
                  setFormData({ ...formData, witness_2_employee_id: e.target.value })
                }
              />
            </div>
          </div>

          <div>
            <Label>Breaking Scheduled Date *</Label>
            <Input
              type="date"
              value={formData.breaking_scheduled_date}
              onChange={(e) =>
                setFormData({ ...formData, breaking_scheduled_date: e.target.value })
              }
            />
          </div>

          <Button onClick={handleSubmit} disabled={isLoading} className="w-full">
            {isLoading ? 'Initiating...' : 'Initiate Breaking'}
          </Button>
        </div>
      </DialogContent>
    </Dialog>
  )
}

// Breaking Details Dialog Component
function BreakingDetailsDialog({
  breaking,
  open,
  onOpenChange,
  onVideographySubmit,
  onInventorySubmit,
  onChargesSubmit,
  onComplete,
}: {
  breaking: BreakingRecord
  open: boolean
  onOpenChange: (open: boolean) => void
  onVideographySubmit: (data: any) => void
  onInventorySubmit: (data: any) => void
  onChargesSubmit: (data: any) => void
  onComplete: (data: any) => void
}) {
  const [activeStep, setActiveStep] = useState('details')

  const steps = [
    { id: 'details', label: 'Details', icon: FileText },
    { id: 'videography', label: 'Videography', icon: Video },
    { id: 'inventory', label: 'Inventory', icon: Package },
    { id: 'charges', label: 'Charges', icon: DollarSign },
  ]

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-4xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>Breaking Details - {breaking.breaking_number}</DialogTitle>
          <DialogDescription>
            Locker ID: {breaking.locker_id} | Status: {breaking.status}
          </DialogDescription>
        </DialogHeader>

        <Tabs value={activeStep} onValueChange={setActiveStep}>
          <TabsList className="grid w-full grid-cols-4">
            {steps.map((step) => (
              <TabsTrigger key={step.id} value={step.id}>
                <step.icon className="h-4 w-4 mr-2" />
                {step.label}
              </TabsTrigger>
            ))}
          </TabsList>

          <TabsContent value="details" className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <Label className="text-muted-foreground">Breaking Reason</Label>
                <p className="font-medium">
                  {breaking.breaking_reason.replace(/_/g, ' ')}
                </p>
              </div>
              <div>
                <Label className="text-muted-foreground">Status</Label>
                <p>{breaking.status}</p>
              </div>
              <div>
                <Label className="text-muted-foreground">Scheduled Date</Label>
                <p>{format(new Date(breaking.breaking_scheduled_date), 'PPP')}</p>
              </div>
              <div>
                <Label className="text-muted-foreground">Actual Date</Label>
                <p>
                  {breaking.breaking_actual_date
                    ? format(new Date(breaking.breaking_actual_date), 'PPP')
                    : 'Not yet broken'}
                </p>
              </div>
            </div>

            <Separator />

            <div>
              <h3 className="font-medium mb-2">Authorization Details</h3>
              <div className="space-y-2 text-sm">
                <p>
                  <strong>Branch Manager:</strong> {breaking.authorized_by_branch_manager}
                </p>
                <p>
                  <strong>Regional Head:</strong> {breaking.authorized_by_regional_head}
                </p>
                {breaking.police_intimation_required && (
                  <Alert>
                    <AlertTriangle className="h-4 w-4" />
                    <AlertDescription>
                      Police intimation required - Station: {breaking.police_station}
                    </AlertDescription>
                  </Alert>
                )}
              </div>
            </div>

            <Separator />

            <div>
              <h3 className="font-medium mb-2">Witnesses</h3>
              <div className="space-y-2">
                <div className="flex items-center gap-2">
                  <Users className="h-4 w-4" />
                  <span>
                    {breaking.witness_1.name} (ID: {breaking.witness_1.employee_id})
                  </span>
                </div>
                <div className="flex items-center gap-2">
                  <Users className="h-4 w-4" />
                  <span>
                    {breaking.witness_2.name} (ID: {breaking.witness_2.employee_id})
                  </span>
                </div>
              </div>
            </div>
          </TabsContent>

          <TabsContent value="videography" className="space-y-4">
            {breaking.videography_done ? (
              <div className="space-y-3">
                <Alert>
                  <CheckCircle className="h-4 w-4" />
                  <AlertDescription>Videography completed successfully</AlertDescription>
                </Alert>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <Label className="text-muted-foreground">Duration</Label>
                    <p>{breaking.videography_duration} minutes</p>
                  </div>
                  <div>
                    <Label className="text-muted-foreground">Videographer</Label>
                    <p>{breaking.videographer_name}</p>
                  </div>
                  <div>
                    <Label className="text-muted-foreground">Start Time</Label>
                    <p>{breaking.videography_start_time}</p>
                  </div>
                  <div>
                    <Label className="text-muted-foreground">End Time</Label>
                    <p>{breaking.videography_end_time}</p>
                  </div>
                </div>
              </div>
            ) : (
              <VideographyForm onSubmit={onVideographySubmit} />
            )}
          </TabsContent>

          <TabsContent value="inventory" className="space-y-4">
            {breaking.inventory_prepared ? (
              <div className="space-y-3">
                <Alert>
                  <CheckCircle className="h-4 w-4" />
                  <AlertDescription>
                    Inventory prepared - {breaking.total_items_count} items
                  </AlertDescription>
                </Alert>
                <div>
                  <h4 className="font-medium mb-2">Inventory Items</h4>
                  <Table>
                    <TableHeader>
                      <TableRow>
                        <TableHead>#</TableHead>
                        <TableHead>Description</TableHead>
                        <TableHead>Quantity</TableHead>
                        <TableHead>Estimated Value</TableHead>
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      {breaking.inventory_items?.map((item: InventoryItem) => (
                        <TableRow key={item.item_number}>
                          <TableCell>{item.item_number}</TableCell>
                          <TableCell>{item.description}</TableCell>
                          <TableCell>{item.quantity}</TableCell>
                          <TableCell>
                            {item.estimated_value
                              ? `₹${item.estimated_value.toLocaleString()}`
                              : '-'}
                          </TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </div>
              </div>
            ) : (
              <InventoryForm onSubmit={onInventorySubmit} />
            )}
          </TabsContent>

          <TabsContent value="charges" className="space-y-4">
            {breaking.total_charges ? (
              <div className="space-y-3">
                <Alert>
                  <CheckCircle className="h-4 w-4" />
                  <AlertDescription>
                    Total charges: ₹{breaking.total_charges.toLocaleString()}
                  </AlertDescription>
                </Alert>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <Label className="text-muted-foreground">Breaking Charges</Label>
                    <p>₹{breaking.breaking_charges.toLocaleString()}</p>
                  </div>
                  <div>
                    <Label className="text-muted-foreground">Lock Replacement</Label>
                    <p>₹{breaking.lock_replacement_charges.toLocaleString()}</p>
                  </div>
                  <div>
                    <Label className="text-muted-foreground">Videography</Label>
                    <p>₹{breaking.videography_charges.toLocaleString()}</p>
                  </div>
                  <div>
                    <Label className="text-muted-foreground">Storage Charges</Label>
                    <p>₹{breaking.storage_charges_per_month.toLocaleString()}/month</p>
                  </div>
                  <div>
                    <Label className="text-muted-foreground">GST ({breaking.gst_rate}%)</Label>
                    <p>₹{breaking.gst_amount.toLocaleString()}</p>
                  </div>
                  <div>
                    <Label className="text-muted-foreground font-bold">Total</Label>
                    <p className="font-bold text-lg">
                      ₹{breaking.total_charges.toLocaleString()}
                    </p>
                  </div>
                </div>
              </div>
            ) : (
              <ChargesForm onSubmit={onChargesSubmit} />
            )}
          </TabsContent>
        </Tabs>

        <Separator />

        {breaking.status !== BreakingStatus.COMPLETED && (
          <div className="flex justify-end gap-2">
            <Button variant="outline" onClick={() => onOpenChange(false)}>
              Close
            </Button>
            {breaking.status === BreakingStatus.CHARGES_CALCULATED && (
              <Button
                onClick={() =>
                  onComplete({
                    completion_date: new Date().toISOString().split('T')[0],
                    certificate_number: `BRK-CERT-${Date.now()}`,
                    customer_notified: true,
                  })
                }
              >
                Complete Breaking
              </Button>
            )}
          </div>
        )}
      </DialogContent>
    </Dialog>
  )
}

// Videography Form Component
function VideographyForm({ onSubmit }: { onSubmit: (data: any) => void }) {
  const [formData, setFormData] = useState({
    videography_start_time: '',
    videography_end_time: '',
    video_file_paths: [''],
    videographer_name: '',
  })

  return (
    <div className="space-y-4">
      <h3 className="font-medium">Record Videography Details</h3>
      <div className="grid grid-cols-2 gap-4">
        <div>
          <Label>Start Time *</Label>
          <Input
            type="time"
            value={formData.videography_start_time}
            onChange={(e) =>
              setFormData({ ...formData, videography_start_time: e.target.value })
            }
          />
        </div>
        <div>
          <Label>End Time *</Label>
          <Input
            type="time"
            value={formData.videography_end_time}
            onChange={(e) =>
              setFormData({ ...formData, videography_end_time: e.target.value })
            }
          />
        </div>
      </div>
      <div>
        <Label>Videographer Name *</Label>
        <Input
          value={formData.videographer_name}
          onChange={(e) => setFormData({ ...formData, videographer_name: e.target.value })}
        />
      </div>
      <div>
        <Label>Video File Path *</Label>
        <Input
          value={formData.video_file_paths[0]}
          onChange={(e) =>
            setFormData({ ...formData, video_file_paths: [e.target.value] })
          }
          placeholder="/storage/videos/breaking_xxxxx.mp4"
        />
      </div>
      <Button onClick={() => onSubmit(formData)} className="w-full">
        Submit Videography
      </Button>
    </div>
  )
}

// Inventory Form Component
function InventoryForm({ onSubmit }: { onSubmit: (data: any) => void }) {
  const [items, setItems] = useState<InventoryItem[]>([
    { item_number: 1, description: '', quantity: 1, estimated_value: 0 },
  ])
  const [preparedBy, setPreparedBy] = useState('')
  const [verifiedBy, setVerifiedBy] = useState('')

  const addItem = () => {
    setItems([
      ...items,
      {
        item_number: items.length + 1,
        description: '',
        quantity: 1,
        estimated_value: 0,
      },
    ])
  }

  const updateItem = (index: number, field: keyof InventoryItem, value: any) => {
    const newItems = [...items]
    newItems[index] = { ...newItems[index], [field]: value }
    setItems(newItems)
  }

  const handleSubmit = () => {
    onSubmit({
      inventory_date: new Date().toISOString().split('T')[0],
      inventory_items: items,
      inventory_prepared_by: preparedBy,
      inventory_verified_by: verifiedBy,
    })
  }

  return (
    <div className="space-y-4">
      <h3 className="font-medium">Prepare Inventory</h3>
      <div className="space-y-3">
        {items.map((item, index) => (
          <div key={index} className="grid grid-cols-4 gap-2 p-3 border rounded">
            <div>
              <Label className="text-xs">Description</Label>
              <Input
                value={item.description}
                onChange={(e) => updateItem(index, 'description', e.target.value)}
                placeholder="Item description"
              />
            </div>
            <div>
              <Label className="text-xs">Quantity</Label>
              <Input
                type="number"
                value={item.quantity}
                onChange={(e) => updateItem(index, 'quantity', parseInt(e.target.value))}
              />
            </div>
            <div>
              <Label className="text-xs">Est. Value (₹)</Label>
              <Input
                type="number"
                value={item.estimated_value}
                onChange={(e) =>
                  updateItem(index, 'estimated_value', parseFloat(e.target.value))
                }
              />
            </div>
            <div>
              <Label className="text-xs">Condition</Label>
              <Input
                value={item.condition || ''}
                onChange={(e) => updateItem(index, 'condition', e.target.value)}
                placeholder="Good/Fair/Poor"
              />
            </div>
          </div>
        ))}
      </div>
      <Button variant="outline" onClick={addItem} size="sm">
        <Plus className="h-4 w-4 mr-1" />
        Add Item
      </Button>
      <div className="grid grid-cols-2 gap-4">
        <div>
          <Label>Prepared By *</Label>
          <Input value={preparedBy} onChange={(e) => setPreparedBy(e.target.value)} />
        </div>
        <div>
          <Label>Verified By *</Label>
          <Input value={verifiedBy} onChange={(e) => setVerifiedBy(e.target.value)} />
        </div>
      </div>
      <Button onClick={handleSubmit} className="w-full">
        Submit Inventory
      </Button>
    </div>
  )
}

// Charges Form Component
function ChargesForm({ onSubmit }: { onSubmit: (data: any) => void }) {
  const [formData, setFormData] = useState({
    breaking_charges: 5000,
    lock_replacement_charges: 2000,
    videography_charges: 3000,
    valuation_charges: 0,
    storage_charges_per_month: 500,
    legal_charges: 0,
    other_charges: 0,
  })

  const calculateTotal = () => {
    const subtotal = Object.values(formData).reduce((a, b) => a + b, 0)
    const gst = subtotal * 0.18
    return { subtotal, gst, total: subtotal + gst }
  }

  const { subtotal, gst, total } = calculateTotal()

  return (
    <div className="space-y-4">
      <h3 className="font-medium">Calculate Breaking Charges</h3>
      <div className="grid grid-cols-2 gap-4">
        <div>
          <Label>Breaking Charges (₹)</Label>
          <Input
            type="number"
            value={formData.breaking_charges}
            onChange={(e) =>
              setFormData({ ...formData, breaking_charges: parseFloat(e.target.value) })
            }
          />
        </div>
        <div>
          <Label>Lock Replacement (₹)</Label>
          <Input
            type="number"
            value={formData.lock_replacement_charges}
            onChange={(e) =>
              setFormData({
                ...formData,
                lock_replacement_charges: parseFloat(e.target.value),
              })
            }
          />
        </div>
        <div>
          <Label>Videography Charges (₹)</Label>
          <Input
            type="number"
            value={formData.videography_charges}
            onChange={(e) =>
              setFormData({ ...formData, videography_charges: parseFloat(e.target.value) })
            }
          />
        </div>
        <div>
          <Label>Storage (₹/month)</Label>
          <Input
            type="number"
            value={formData.storage_charges_per_month}
            onChange={(e) =>
              setFormData({
                ...formData,
                storage_charges_per_month: parseFloat(e.target.value),
              })
            }
          />
        </div>
        <div>
          <Label>Valuation Charges (₹)</Label>
          <Input
            type="number"
            value={formData.valuation_charges}
            onChange={(e) =>
              setFormData({ ...formData, valuation_charges: parseFloat(e.target.value) })
            }
          />
        </div>
        <div>
          <Label>Other Charges (₹)</Label>
          <Input
            type="number"
            value={formData.other_charges}
            onChange={(e) =>
              setFormData({ ...formData, other_charges: parseFloat(e.target.value) })
            }
          />
        </div>
      </div>

      <Separator />

      <div className="space-y-2 bg-muted p-4 rounded">
        <div className="flex justify-between">
          <span>Subtotal:</span>
          <span className="font-medium">₹{subtotal.toLocaleString()}</span>
        </div>
        <div className="flex justify-between">
          <span>GST (18%):</span>
          <span className="font-medium">₹{gst.toLocaleString()}</span>
        </div>
        <Separator />
        <div className="flex justify-between text-lg">
          <span className="font-bold">Total:</span>
          <span className="font-bold">₹{total.toLocaleString()}</span>
        </div>
      </div>

      <Button onClick={() => onSubmit(formData)} className="w-full">
        Calculate & Save Charges
      </Button>
    </div>
  )
}
