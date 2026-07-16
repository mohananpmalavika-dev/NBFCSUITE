'use client'

/**
 * Locker Maintenance Management Page
 * Handles preventive and breakdown maintenance operations
 */

import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Plus, Wrench, Calendar, AlertCircle, CheckCircle, Filter, Download } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Badge } from '@/components/ui/badge'
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from '@/components/ui/dialog'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Textarea } from '@/components/ui/textarea'
import { useToast } from '@/components/ui/use-toast'
import { 
  maintenanceService, 
  type MaintenanceRecord, 
  type MaintenanceStatistics,
  MaintenanceType,
  MaintenanceStatus,
  MaintenancePriority,
  MaintenanceCategory,
  CleaningType,
  LockJammingCause,
  KeyReplacementAction,
  RecurringFrequency 
} from '@/services/locker.service'
import { DataTable } from '@/components/ui/data-table'
import { formatDate, formatCurrency } from '@/lib/utils'


export default function MaintenanceManagementPage() {
  const { toast } = useToast()
  const queryClient = useQueryClient()
  
  // State management
  const [activeTab, setActiveTab] = useState('overview')
  const [scheduleDialogOpen, setScheduleDialogOpen] = useState(false)
  const [reportDialogOpen, setReportDialogOpen] = useState(false)
  const [detailsDialogOpen, setDetailsDialogOpen] = useState(false)
  const [selectedMaintenance, setSelectedMaintenance] = useState<MaintenanceRecord | null>(null)
  
  // Fetch statistics
  const { data: statistics } = useQuery<MaintenanceStatistics>({
    queryKey: ['maintenance', 'statistics'],
    queryFn: async () => {
      const response = await maintenanceService.getStatistics()
      return response.data
    }
  })
  
  // Fetch maintenance records
  const { data: maintenanceData, isLoading } = useQuery({
    queryKey: ['maintenance', 'records', activeTab],
    queryFn: async () => {
      let status: MaintenanceStatus | undefined
      if (activeTab === 'scheduled') status = MaintenanceStatus.SCHEDULED
      else if (activeTab === 'in-progress') status = MaintenanceStatus.IN_PROGRESS
      else if (activeTab === 'completed') status = MaintenanceStatus.COMPLETED
      
      const response = await maintenanceService.listMaintenanceRecords({ status })
      return response.data
    }
  })
  
  // Fetch upcoming maintenance
  const { data: upcomingData } = useQuery({
    queryKey: ['maintenance', 'upcoming'],
    queryFn: async () => {
      const response = await maintenanceService.getUpcomingMaintenance(30)
      return response.data.upcoming_maintenance
    }
  })
  
  // Fetch overdue maintenance
  const { data: overdueData } = useQuery({
    queryKey: ['maintenance', 'overdue'],
    queryFn: async () => {
      const response = await maintenanceService.getOverdueMaintenance()
      return response.data.overdue_maintenance
    }
  })
  
  // Fetch pending breakdowns
  const { data: breakdownsData } = useQuery({
    queryKey: ['maintenance', 'breakdowns'],
    queryFn: async () => {
      const response = await maintenanceService.getPendingBreakdowns()
      return response.data.pending_breakdowns
    }
  })
  
  const handleViewDetails = (maintenance: MaintenanceRecord) => {
    setSelectedMaintenance(maintenance)
    setDetailsDialogOpen(true)
  }
  
  const handleScheduleSuccess = () => {
    queryClient.invalidateQueries({ queryKey: ['maintenance'] })
    setScheduleDialogOpen(false)
    toast({
      title: 'Success',
      description: 'Preventive maintenance scheduled successfully'
    })
  }
  
  const handleReportSuccess = () => {
    queryClient.invalidateQueries({ queryKey: ['maintenance'] })
    setReportDialogOpen(false)
    toast({
      title: 'Success',
      description: 'Breakdown reported successfully'
    })
  }
  
  return (
    <div className="container mx-auto py-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Locker Maintenance</h1>
          <p className="text-muted-foreground">
            Manage preventive and breakdown maintenance operations
          </p>
        </div>
        <div className="flex gap-2">
          <Button onClick={() => setReportDialogOpen(true)} variant="outline">
            <AlertCircle className="mr-2 h-4 w-4" />
            Report Breakdown
          </Button>
          <Button onClick={() => setScheduleDialogOpen(true)}>
            <Plus className="mr-2 h-4 w-4" />
            Schedule Maintenance
          </Button>
        </div>
      </div>
      
      {/* Statistics Dashboard */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Maintenance</CardTitle>
            <Wrench className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{statistics?.total_maintenance || 0}</div>
            <p className="text-xs text-muted-foreground">
              {statistics?.preventive_maintenance || 0} preventive, {statistics?.breakdown_maintenance || 0} breakdown
            </p>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Scheduled</CardTitle>
            <Calendar className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{statistics?.scheduled || 0}</div>
            <p className="text-xs text-muted-foreground">
              {upcomingData?.length || 0} upcoming, {overdueData?.length || 0} overdue
            </p>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Pending Breakdowns</CardTitle>
            <AlertCircle className="h-4 w-4 text-destructive" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-destructive">{breakdownsData?.length || 0}</div>
            <p className="text-xs text-muted-foreground">
              Requires immediate attention
            </p>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Cost</CardTitle>
            <CheckCircle className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{formatCurrency(statistics?.total_cost || 0)}</div>
            <p className="text-xs text-muted-foreground">
              Customer charges: {formatCurrency(statistics?.customer_charges_collected || 0)}
            </p>
          </CardContent>
        </Card>
      </div>
      
      {/* Maintenance Records Tabs */}
      <Card>
        <CardHeader>
          <CardTitle>Maintenance Records</CardTitle>
          <CardDescription>View and manage all maintenance activities</CardDescription>
        </CardHeader>
        <CardContent>
          <Tabs value={activeTab} onValueChange={setActiveTab}>
            <TabsList>
              <TabsTrigger value="overview">Overview</TabsTrigger>
              <TabsTrigger value="scheduled">Scheduled</TabsTrigger>
              <TabsTrigger value="in-progress">In Progress</TabsTrigger>
              <TabsTrigger value="overdue">Overdue</TabsTrigger>
              <TabsTrigger value="breakdowns">Breakdowns</TabsTrigger>
              <TabsTrigger value="completed">Completed</TabsTrigger>
              <TabsTrigger value="all">All Records</TabsTrigger>
            </TabsList>
            
            <TabsContent value="overview" className="space-y-4">
              <MaintenanceOverview
                upcoming={upcomingData || []}
                overdue={overdueData || []}
                breakdowns={breakdownsData || []}
                onViewDetails={handleViewDetails}
              />
            </TabsContent>
            
            <TabsContent value="scheduled">
              <MaintenanceTable
                data={maintenanceData?.records || []}
                isLoading={isLoading}
                onViewDetails={handleViewDetails}
              />
            </TabsContent>
            
            <TabsContent value="in-progress">
              <MaintenanceTable
                data={maintenanceData?.records || []}
                isLoading={isLoading}
                onViewDetails={handleViewDetails}
              />
            </TabsContent>
            
            <TabsContent value="overdue">
              <MaintenanceTable
                data={overdueData || []}
                isLoading={isLoading}
                onViewDetails={handleViewDetails}
              />
            </TabsContent>
            
            <TabsContent value="breakdowns">
              <MaintenanceTable
                data={breakdownsData || []}
                isLoading={isLoading}
                onViewDetails={handleViewDetails}
              />
            </TabsContent>
            
            <TabsContent value="completed">
              <MaintenanceTable
                data={maintenanceData?.records || []}
                isLoading={isLoading}
                onViewDetails={handleViewDetails}
              />
            </TabsContent>
            
            <TabsContent value="all">
              <MaintenanceTable
                data={maintenanceData?.records || []}
                isLoading={isLoading}
                onViewDetails={handleViewDetails}
              />
            </TabsContent>
          </Tabs>
        </CardContent>
      </Card>
      
      {/* Schedule Preventive Maintenance Dialog */}
      <ScheduleMaintenanceDialog
        open={scheduleDialogOpen}
        onOpenChange={setScheduleDialogOpen}
        onSuccess={handleScheduleSuccess}
      />
      
      {/* Report Breakdown Dialog */}
      <ReportBreakdownDialog
        open={reportDialogOpen}
        onOpenChange={setReportDialogOpen}
        onSuccess={handleReportSuccess}
      />
      
      {/* Maintenance Details Dialog */}
      {selectedMaintenance && (
        <MaintenanceDetailsDialog
          open={detailsDialogOpen}
          onOpenChange={setDetailsDialogOpen}
          maintenance={selectedMaintenance}
          onUpdate={() => queryClient.invalidateQueries({ queryKey: ['maintenance'] })}
        />
      )}
    </div>
  )
}


// Maintenance Overview Component
function MaintenanceOverview({
  upcoming,
  overdue,
  breakdowns,
  onViewDetails
}: {
  upcoming: MaintenanceRecord[]
  overdue: MaintenanceRecord[]
  breakdowns: MaintenanceRecord[]
  onViewDetails: (maintenance: MaintenanceRecord) => void
}) {
  return (
    <div className="space-y-4">
      {/* Overdue Maintenance - Highest Priority */}
      {overdue.length > 0 && (
        <Card className="border-destructive">
          <CardHeader>
            <CardTitle className="text-destructive flex items-center gap-2">
              <AlertCircle className="h-5 w-5" />
              Overdue Maintenance ({overdue.length})
            </CardTitle>
            <CardDescription>Maintenance tasks past their scheduled date</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              {overdue.slice(0, 5).map((maintenance) => (
                <div
                  key={maintenance.id}
                  className="flex items-center justify-between p-3 border rounded-lg hover:bg-accent cursor-pointer"
                  onClick={() => onViewDetails(maintenance)}
                >
                  <div className="space-y-1">
                    <p className="font-medium">{maintenance.maintenance_number}</p>
                    <p className="text-sm text-muted-foreground">
                      {maintenance.maintenance_type} - {maintenance.locker_id}
                    </p>
                  </div>
                  <div className="text-right">
                    <Badge variant="destructive">{maintenance.priority}</Badge>
                    <p className="text-xs text-muted-foreground mt-1">
                      Due: {formatDate(maintenance.scheduled_date)}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}
      
      {/* Pending Breakdowns */}
      {breakdowns.length > 0 && (
        <Card className="border-orange-500">
          <CardHeader>
            <CardTitle className="text-orange-500 flex items-center gap-2">
              <Wrench className="h-5 w-5" />
              Pending Breakdowns ({breakdowns.length})
            </CardTitle>
            <CardDescription>Breakdown maintenance requiring attention</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              {breakdowns.slice(0, 5).map((maintenance) => (
                <div
                  key={maintenance.id}
                  className="flex items-center justify-between p-3 border rounded-lg hover:bg-accent cursor-pointer"
                  onClick={() => onViewDetails(maintenance)}
                >
                  <div className="space-y-1">
                    <p className="font-medium">{maintenance.maintenance_number}</p>
                    <p className="text-sm text-muted-foreground">
                      {maintenance.maintenance_type} - {maintenance.locker_id}
                    </p>
                  </div>
                  <div className="text-right">
                    <Badge variant="outline" className="border-orange-500 text-orange-500">
                      {maintenance.priority}
                    </Badge>
                    <p className="text-xs text-muted-foreground mt-1">
                      Reported: {formatDate(maintenance.created_at)}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}
      
      {/* Upcoming Maintenance */}
      {upcoming.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Calendar className="h-5 w-5" />
              Upcoming Maintenance (Next 30 Days)
            </CardTitle>
            <CardDescription>{upcoming.length} tasks scheduled</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              {upcoming.slice(0, 5).map((maintenance) => (
                <div
                  key={maintenance.id}
                  className="flex items-center justify-between p-3 border rounded-lg hover:bg-accent cursor-pointer"
                  onClick={() => onViewDetails(maintenance)}
                >
                  <div className="space-y-1">
                    <p className="font-medium">{maintenance.maintenance_number}</p>
                    <p className="text-sm text-muted-foreground">
                      {maintenance.maintenance_type} - {maintenance.locker_id}
                    </p>
                  </div>
                  <div className="text-right">
                    <Badge>{maintenance.priority}</Badge>
                    <p className="text-xs text-muted-foreground mt-1">
                      Due: {formatDate(maintenance.scheduled_date)}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  )
}


// Maintenance Table Component
function MaintenanceTable({
  data,
  isLoading,
  onViewDetails
}: {
  data: MaintenanceRecord[]
  isLoading: boolean
  onViewDetails: (maintenance: MaintenanceRecord) => void
}) {
  const columns = [
    {
      accessorKey: 'maintenance_number',
      header: 'Maintenance #'
    },
    {
      accessorKey: 'locker_id',
      header: 'Locker'
    },
    {
      accessorKey: 'maintenance_type',
      header: 'Type',
      cell: ({ row }: any) => (
        <span className="capitalize">{row.original.maintenance_type.replace(/_/g, ' ')}</span>
      )
    },
    {
      accessorKey: 'maintenance_category',
      header: 'Category',
      cell: ({ row }: any) => (
        <Badge variant="outline">{row.original.maintenance_category}</Badge>
      )
    },
    {
      accessorKey: 'priority',
      header: 'Priority',
      cell: ({ row }: any) => {
        const priority = row.original.priority
        const variant = priority === 'urgent' || priority === 'emergency' ? 'destructive' : 'default'
        return <Badge variant={variant}>{priority}</Badge>
      }
    },
    {
      accessorKey: 'scheduled_date',
      header: 'Scheduled Date',
      cell: ({ row }: any) => formatDate(row.original.scheduled_date)
    },
    {
      accessorKey: 'status',
      header: 'Status',
      cell: ({ row }: any) => {
        const status = row.original.status
        let variant: 'default' | 'secondary' | 'destructive' | 'outline' = 'default'
        if (status === 'completed') variant = 'default'
        else if (status === 'in_progress') variant = 'secondary'
        else if (status === 'cancelled' || status === 'failed') variant = 'destructive'
        return <Badge variant={variant}>{status}</Badge>
      }
    },
    {
      id: 'actions',
      cell: ({ row }: any) => (
        <Button variant="ghost" size="sm" onClick={() => onViewDetails(row.original)}>
          View
        </Button>
      )
    }
  ]
  
  if (isLoading) {
    return <div className="text-center py-8">Loading...</div>
  }
  
  if (!data || data.length === 0) {
    return <div className="text-center py-8 text-muted-foreground">No maintenance records found</div>
  }
  
  return <DataTable columns={columns} data={data} />
}


// Schedule Maintenance Dialog - FULL IMPLEMENTATION
function ScheduleMaintenanceDialog({
  open,
  onOpenChange,
  onSuccess
}: {
  open: boolean
  onOpenChange: (open: boolean) => void
  onSuccess: () => void
}) {
  const [formData, setFormData] = useState({
    locker_id: '',
    branch_id: '',
    maintenance_type: MaintenanceType.LOCK_SERVICING,
    scheduled_date: '',
    scheduled_time: '',
    is_recurring: false,
    recurring_frequency: RecurringFrequency.QUARTERLY,
    assigned_to: '',
    description: ''
  })
  
  const scheduleMutation = useMutation({
    mutationFn: (data: any) => maintenanceService.schedulePreventiveMaintenance(data),
    onSuccess: () => {
      onSuccess()
      setFormData({
        locker_id: '',
        branch_id: '',
        maintenance_type: MaintenanceType.LOCK_SERVICING,
        scheduled_date: '',
        scheduled_time: '',
        is_recurring: false,
        recurring_frequency: RecurringFrequency.QUARTERLY,
        assigned_to: '',
        description: ''
      })
    },
    onError: (error: any) => {
      toast({
        title: 'Error',
        description: error.message || 'Failed to schedule maintenance',
        variant: 'destructive'
      })
    }
  })
  
  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    
    // Validation
    if (!formData.locker_id || !formData.scheduled_date || !formData.assigned_to) {
      toast({
        title: 'Validation Error',
        description: 'Please fill in all required fields',
        variant: 'destructive'
      })
      return
    }
    
    if (formData.is_recurring && !formData.recurring_frequency) {
      toast({
        title: 'Validation Error',
        description: 'Recurring frequency is required when recurring is enabled',
        variant: 'destructive'
      })
      return
    }
    
    scheduleMutation.mutate(formData)
  }
  
  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>Schedule Preventive Maintenance</DialogTitle>
          <DialogDescription>Schedule routine maintenance for locker</DialogDescription>
        </DialogHeader>
        
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="grid grid-cols-2 gap-4">
            {/* Locker Selection */}
            <div className="col-span-2">
              <Label htmlFor="locker_id">Locker <span className="text-destructive">*</span></Label>
              <Input
                id="locker_id"
                placeholder="Search locker by number..."
                value={formData.locker_id}
                onChange={(e) => setFormData({ ...formData, locker_id: e.target.value })}
                required
              />
            </div>
            
            {/* Maintenance Type */}
            <div>
              <Label htmlFor="maintenance_type">Maintenance Type <span className="text-destructive">*</span></Label>
              <Select
                value={formData.maintenance_type}
                onValueChange={(value) => setFormData({ ...formData, maintenance_type: value as MaintenanceType })}
              >
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value={MaintenanceType.LOCK_SERVICING}>Lock Servicing</SelectItem>
                  <SelectItem value={MaintenanceType.KEY_DUPLICATION}>Key Duplication</SelectItem>
                  <SelectItem value={MaintenanceType.LOCKER_CLEANING}>Locker Cleaning</SelectItem>
                  <SelectItem value={MaintenanceType.VAULT_MAINTENANCE}>Vault Maintenance</SelectItem>
                  <SelectItem value={MaintenanceType.FIRE_PROTECTION_CHECK}>Fire Protection Check</SelectItem>
                </SelectContent>
              </Select>
            </div>
            
            {/* Scheduled Date */}
            <div>
              <Label htmlFor="scheduled_date">Scheduled Date <span className="text-destructive">*</span></Label>
              <Input
                id="scheduled_date"
                type="date"
                value={formData.scheduled_date}
                onChange={(e) => setFormData({ ...formData, scheduled_date: e.target.value })}
                min={new Date().toISOString().split('T')[0]}
                required
              />
            </div>
            
            {/* Scheduled Time */}
            <div>
              <Label htmlFor="scheduled_time">Scheduled Time</Label>
              <Input
                id="scheduled_time"
                type="time"
                value={formData.scheduled_time}
                onChange={(e) => setFormData({ ...formData, scheduled_time: e.target.value })}
              />
            </div>
            
            {/* Assigned To */}
            <div>
              <Label htmlFor="assigned_to">Assigned To <span className="text-destructive">*</span></Label>
              <Input
                id="assigned_to"
                placeholder="Technician name or ID"
                value={formData.assigned_to}
                onChange={(e) => setFormData({ ...formData, assigned_to: e.target.value })}
                required
              />
            </div>
            
            {/* Recurring Checkbox */}
            <div className="col-span-2 flex items-center space-x-2">
              <input
                type="checkbox"
                id="is_recurring"
                checked={formData.is_recurring}
                onChange={(e) => setFormData({ ...formData, is_recurring: e.target.checked })}
                className="rounded border-gray-300"
              />
              <Label htmlFor="is_recurring" className="cursor-pointer">
                Schedule as recurring maintenance
              </Label>
            </div>
            
            {/* Recurring Frequency */}
            {formData.is_recurring && (
              <div className="col-span-2">
                <Label htmlFor="recurring_frequency">Recurring Frequency <span className="text-destructive">*</span></Label>
                <Select
                  value={formData.recurring_frequency}
                  onValueChange={(value) => setFormData({ ...formData, recurring_frequency: value as RecurringFrequency })}
                >
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value={RecurringFrequency.MONTHLY}>Monthly</SelectItem>
                    <SelectItem value={RecurringFrequency.QUARTERLY}>Quarterly</SelectItem>
                    <SelectItem value={RecurringFrequency.SEMI_ANNUAL}>Semi-Annual</SelectItem>
                    <SelectItem value={RecurringFrequency.ANNUAL}>Annual</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            )}
            
            {/* Description */}
            <div className="col-span-2">
              <Label htmlFor="description">Description</Label>
              <Textarea
                id="description"
                placeholder="Additional notes or instructions..."
                value={formData.description}
                onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                rows={3}
                maxLength={500}
              />
              <p className="text-xs text-muted-foreground mt-1">
                {formData.description.length}/500 characters
              </p>
            </div>
          </div>
          
          <DialogFooter>
            <Button type="button" variant="outline" onClick={() => onOpenChange(false)}>
              Cancel
            </Button>
            <Button type="submit" disabled={scheduleMutation.isPending}>
              {scheduleMutation.isPending ? 'Scheduling...' : 'Schedule Maintenance'}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  )
}


// Report Breakdown Dialog - FULL IMPLEMENTATION
function ReportBreakdownDialog({
  open,
  onOpenChange,
  onSuccess
}: {
  open: boolean
  onOpenChange: (open: boolean) => void
  onSuccess: () => void
}) {
  const { toast } = useToast()
  const [formData, setFormData] = useState({
    locker_id: '',
    branch_id: '',
    maintenance_type: MaintenanceType.LOCK_JAMMING,
    priority: MaintenancePriority.MEDIUM,
    description: '',
    customer_reported: false,
    customer_id: '',
    assigned_to: ''
  })
  
  const reportMutation = useMutation({
    mutationFn: (data: any) => maintenanceService.reportBreakdown(data),
    onSuccess: () => {
      onSuccess()
      setFormData({
        locker_id: '',
        branch_id: '',
        maintenance_type: MaintenanceType.LOCK_JAMMING,
        priority: MaintenancePriority.MEDIUM,
        description: '',
        customer_reported: false,
        customer_id: '',
        assigned_to: ''
      })
    },
    onError: (error: any) => {
      toast({
        title: 'Error',
        description: error.message || 'Failed to report breakdown',
        variant: 'destructive'
      })
    }
  })
  
  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    
    // Validation
    if (!formData.locker_id || !formData.description || !formData.assigned_to) {
      toast({
        title: 'Validation Error',
        description: 'Please fill in all required fields',
        variant: 'destructive'
      })
      return
    }
    
    if (formData.description.length < 10) {
      toast({
        title: 'Validation Error',
        description: 'Description must be at least 10 characters',
        variant: 'destructive'
      })
      return
    }
    
    if (formData.customer_reported && !formData.customer_id) {
      toast({
        title: 'Validation Error',
        description: 'Customer ID is required when customer reported',
        variant: 'destructive'
      })
      return
    }
    
    // Show warning for urgent/emergency
    if (formData.priority === MaintenancePriority.URGENT || formData.priority === MaintenancePriority.EMERGENCY) {
      if (!confirm(`This is marked as ${formData.priority.toUpperCase()} priority. Immediate action required. Continue?`)) {
        return
      }
    }
    
    reportMutation.mutate(formData)
  }
  
  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>Report Breakdown Maintenance</DialogTitle>
          <DialogDescription>Report a locker breakdown or emergency issue</DialogDescription>
        </DialogHeader>
        
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="grid grid-cols-2 gap-4">
            {/* Locker Selection */}
            <div className="col-span-2">
              <Label htmlFor="locker_id">Locker <span className="text-destructive">*</span></Label>
              <Input
                id="locker_id"
                placeholder="Search locker by number..."
                value={formData.locker_id}
                onChange={(e) => setFormData({ ...formData, locker_id: e.target.value })}
                required
              />
            </div>
            
            {/* Issue Type */}
            <div>
              <Label htmlFor="maintenance_type">Issue Type <span className="text-destructive">*</span></Label>
              <Select
                value={formData.maintenance_type}
                onValueChange={(value) => setFormData({ ...formData, maintenance_type: value as MaintenanceType })}
              >
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value={MaintenanceType.LOCK_JAMMING}>Lock Jamming</SelectItem>
                  <SelectItem value={MaintenanceType.KEY_LOST}>Key Lost by Customer</SelectItem>
                  <SelectItem value={MaintenanceType.LOCK_REPLACEMENT}>Lock Replacement</SelectItem>
                  <SelectItem value={MaintenanceType.MASTER_KEY_REGENERATION}>Master Key Regeneration</SelectItem>
                  <SelectItem value={MaintenanceType.LOCKER_REPAIR}>Locker Repair</SelectItem>
                  <SelectItem value={MaintenanceType.OTHER}>Other</SelectItem>
                </SelectContent>
              </Select>
            </div>
            
            {/* Priority */}
            <div>
              <Label htmlFor="priority">Priority <span className="text-destructive">*</span></Label>
              <Select
                value={formData.priority}
                onValueChange={(value) => setFormData({ ...formData, priority: value as MaintenancePriority })}
              >
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value={MaintenancePriority.LOW}>Low</SelectItem>
                  <SelectItem value={MaintenancePriority.MEDIUM}>Medium</SelectItem>
                  <SelectItem value={MaintenancePriority.HIGH}>High</SelectItem>
                  <SelectItem value={MaintenancePriority.URGENT}>Urgent ⚠️</SelectItem>
                  <SelectItem value={MaintenancePriority.EMERGENCY}>Emergency 🚨</SelectItem>
                </SelectContent>
              </Select>
            </div>
            
            {/* Priority Warning */}
            {(formData.priority === MaintenancePriority.URGENT || formData.priority === MaintenancePriority.EMERGENCY) && (
              <div className="col-span-2 p-3 bg-destructive/10 border border-destructive rounded-md">
                <p className="text-sm text-destructive font-medium flex items-center gap-2">
                  <AlertCircle className="h-4 w-4" />
                  {formData.priority === MaintenancePriority.EMERGENCY ? 'EMERGENCY' : 'URGENT'} Priority - Immediate action required!
                </p>
              </div>
            )}
            
            {/* Description */}
            <div className="col-span-2">
              <Label htmlFor="description">Issue Description <span className="text-destructive">*</span></Label>
              <Textarea
                id="description"
                placeholder="Describe the issue in detail (minimum 10 characters)..."
                value={formData.description}
                onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                rows={4}
                maxLength={1000}
                required
              />
              <p className="text-xs text-muted-foreground mt-1">
                {formData.description.length}/1000 characters (min 10 required)
              </p>
            </div>
            
            {/* Customer Reported */}
            <div className="col-span-2 flex items-center space-x-2">
              <input
                type="checkbox"
                id="customer_reported"
                checked={formData.customer_reported}
                onChange={(e) => setFormData({ ...formData, customer_reported: e.target.checked })}
                className="rounded border-gray-300"
              />
              <Label htmlFor="customer_reported" className="cursor-pointer">
                Reported by customer
              </Label>
            </div>
            
            {/* Customer ID */}
            {formData.customer_reported && (
              <div className="col-span-2">
                <Label htmlFor="customer_id">Customer ID <span className="text-destructive">*</span></Label>
                <Input
                  id="customer_id"
                  placeholder="Enter customer ID..."
                  value={formData.customer_id}
                  onChange={(e) => setFormData({ ...formData, customer_id: e.target.value })}
                  required
                />
              </div>
            )}
            
            {/* Assigned To */}
            <div className="col-span-2">
              <Label htmlFor="assigned_to">Assign To <span className="text-destructive">*</span></Label>
              <Input
                id="assigned_to"
                placeholder="Technician name or ID for immediate assignment"
                value={formData.assigned_to}
                onChange={(e) => setFormData({ ...formData, assigned_to: e.target.value })}
                required
              />
            </div>
          </div>
          
          <DialogFooter>
            <Button type="button" variant="outline" onClick={() => onOpenChange(false)}>
              Cancel
            </Button>
            <Button 
              type="submit" 
              disabled={reportMutation.isPending}
              variant={formData.priority === MaintenancePriority.EMERGENCY ? 'destructive' : 'default'}
            >
              {reportMutation.isPending ? 'Reporting...' : 'Report Breakdown'}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  )
}


// Maintenance Details Dialog - COMPLETE IMPLEMENTATION WITH ALL TABS
function MaintenanceDetailsDialog({
  open,
  onOpenChange,
  maintenance,
  onUpdate
}: {
  open: boolean
  onOpenChange: (open: boolean) => void
  maintenance: MaintenanceRecord
  onUpdate: () => void
}) {
  const { toast } = useToast()
  const [activeTab, setActiveTab] = useState('details')
  
  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-6xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle className="flex items-center justify-between">
            <span>Maintenance Details - {maintenance.maintenance_number}</span>
            <Badge variant={maintenance.status === 'completed' ? 'default' : 'secondary'}>
              {maintenance.status}
            </Badge>
          </DialogTitle>
          <DialogDescription>
            {maintenance.maintenance_category} - {maintenance.maintenance_type.replace(/_/g, ' ')}
          </DialogDescription>
        </DialogHeader>
        
        <Tabs value={activeTab} onValueChange={setActiveTab}>
          <TabsList className="grid w-full grid-cols-4">
            <TabsTrigger value="details">Details</TabsTrigger>
            <TabsTrigger value="action" disabled={maintenance.status === 'completed'}>Action</TabsTrigger>
            <TabsTrigger value="cost">Cost</TabsTrigger>
            <TabsTrigger value="completion" disabled={maintenance.status !== 'in_progress'}>Completion</TabsTrigger>
          </TabsList>
          
          <TabsContent value="details">
            <MaintenanceDetailsTab maintenance={maintenance} />
          </TabsContent>
          
          <TabsContent value="action">
            <MaintenanceActionTab maintenance={maintenance} onUpdate={onUpdate} />
          </TabsContent>
          
          <TabsContent value="cost">
            <MaintenanceCostTab maintenance={maintenance} onUpdate={onUpdate} />
          </TabsContent>
          
          <TabsContent value="completion">
            <MaintenanceCompletionTab maintenance={maintenance} onUpdate={onUpdate} onClose={() => onOpenChange(false)} />
          </TabsContent>
        </Tabs>
      </DialogContent>
    </Dialog>
  )
}


// Tab 1: Details (Read-only)
function MaintenanceDetailsTab({ maintenance }: { maintenance: MaintenanceRecord }) {
  return (
    <div className="space-y-6 py-4">
      {/* Basic Information */}
      <div>
        <h3 className="text-lg font-semibold mb-3">Basic Information</h3>
        <div className="grid grid-cols-3 gap-4">
          <div>
            <Label className="text-muted-foreground">Maintenance Number</Label>
            <p className="font-medium">{maintenance.maintenance_number}</p>
          </div>
          <div>
            <Label className="text-muted-foreground">Type</Label>
            <p className="font-medium capitalize">{maintenance.maintenance_type.replace(/_/g, ' ')}</p>
          </div>
          <div>
            <Label className="text-muted-foreground">Category</Label>
            <Badge>{maintenance.maintenance_category}</Badge>
          </div>
          <div>
            <Label className="text-muted-foreground">Priority</Label>
            <Badge variant={maintenance.priority === 'urgent' || maintenance.priority === 'emergency' ? 'destructive' : 'default'}>
              {maintenance.priority}
            </Badge>
          </div>
          <div>
            <Label className="text-muted-foreground">Status</Label>
            <Badge variant="outline">{maintenance.status}</Badge>
          </div>
          <div>
            <Label className="text-muted-foreground">Locker</Label>
            <p className="font-medium">{maintenance.locker_id}</p>
          </div>
        </div>
      </div>
      
      {/* Schedule Information */}
      <div>
        <h3 className="text-lg font-semibold mb-3">Schedule Information</h3>
        <div className="grid grid-cols-3 gap-4">
          <div>
            <Label className="text-muted-foreground">Scheduled Date</Label>
            <p className="font-medium">{formatDate(maintenance.scheduled_date)}</p>
          </div>
          {maintenance.started_date && (
            <div>
              <Label className="text-muted-foreground">Started Date</Label>
              <p className="font-medium">{formatDate(maintenance.started_date)}</p>
            </div>
          )}
          {maintenance.completed_date && (
            <div>
              <Label className="text-muted-foreground">Completed Date</Label>
              <p className="font-medium">{formatDate(maintenance.completed_date)}</p>
            </div>
          )}
          <div>
            <Label className="text-muted-foreground">Assigned To</Label>
            <p className="font-medium">{maintenance.assigned_to || 'Not assigned'}</p>
          </div>
          {maintenance.is_recurring && (
            <>
              <div>
                <Label className="text-muted-foreground">Recurring</Label>
                <Badge variant="secondary">Yes ({maintenance.recurring_frequency})</Badge>
              </div>
              {maintenance.next_scheduled_date && (
                <div>
                  <Label className="text-muted-foreground">Next Scheduled</Label>
                  <p className="font-medium">{formatDate(maintenance.next_scheduled_date)}</p>
                </div>
              )}
            </>
          )}
        </div>
      </div>
      
      {/* Description & Findings */}
      {(maintenance.description || maintenance.findings) && (
        <div>
          <h3 className="text-lg font-semibold mb-3">Notes</h3>
          {maintenance.description && (
            <div className="mb-3">
              <Label className="text-muted-foreground">Description</Label>
              <p className="text-sm mt-1 p-3 bg-muted rounded">{maintenance.description}</p>
            </div>
          )}
          {maintenance.findings && (
            <div>
              <Label className="text-muted-foreground">Findings</Label>
              <p className="text-sm mt-1 p-3 bg-muted rounded">{maintenance.findings}</p>
            </div>
          )}
        </div>
      )}
      
      {/* Cost Summary */}
      <div>
        <h3 className="text-lg font-semibold mb-3">Cost Summary</h3>
        <div className="grid grid-cols-4 gap-4">
          <div>
            <Label className="text-muted-foreground">Labor Cost</Label>
            <p className="font-medium">{formatCurrency(maintenance.labor_cost || 0)}</p>
          </div>
          <div>
            <Label className="text-muted-foreground">Material Cost</Label>
            <p className="font-medium">{formatCurrency(maintenance.material_cost || 0)}</p>
          </div>
          <div>
            <Label className="text-muted-foreground">External Service</Label>
            <p className="font-medium">{formatCurrency(maintenance.external_service_cost || 0)}</p>
          </div>
          <div>
            <Label className="text-muted-foreground">Total Cost</Label>
            <p className="font-bold text-lg">{formatCurrency(maintenance.total_maintenance_cost || 0)}</p>
          </div>
        </div>
        
        {maintenance.customer_charged && (
          <div className="mt-4 p-3 bg-orange-50 border border-orange-200 rounded">
            <Label className="text-muted-foreground">Customer Charges</Label>
            <div className="grid grid-cols-3 gap-4 mt-2">
              <div>
                <p className="text-sm text-muted-foreground">Amount</p>
                <p className="font-medium">{formatCurrency(maintenance.customer_charge_amount || 0)}</p>
              </div>
              <div>
                <p className="text-sm text-muted-foreground">GST (18%)</p>
                <p className="font-medium">{formatCurrency(maintenance.customer_charge_gst_amount || 0)}</p>
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Total</p>
                <p className="font-bold">{formatCurrency(maintenance.customer_total_charge || 0)}</p>
              </div>
              {maintenance.customer_charge_reason && (
                <div className="col-span-3">
                  <p className="text-sm text-muted-foreground">Reason</p>
                  <p className="text-sm">{maintenance.customer_charge_reason}</p>
                </div>
              )}
            </div>
          </div>
        )}
      </div>
      
      {/* Quality & Satisfaction */}
      {maintenance.quality_check_done && (
        <div>
          <h3 className="text-lg font-semibold mb-3">Quality & Satisfaction</h3>
          <div className="grid grid-cols-3 gap-4">
            <div>
              <Label className="text-muted-foreground">Quality Check</Label>
              <Badge variant={maintenance.quality_check_passed ? 'default' : 'destructive'}>
                {maintenance.quality_check_passed ? 'Passed' : 'Failed'}
              </Badge>
            </div>
            <div>
              <Label className="text-muted-foreground">Checked By</Label>
              <p className="font-medium">{maintenance.quality_check_by || 'N/A'}</p>
            </div>
            {maintenance.customer_satisfaction_rating && (
              <div>
                <Label className="text-muted-foreground">Customer Rating</Label>
                <p className="font-medium">{'⭐'.repeat(maintenance.customer_satisfaction_rating)} ({maintenance.customer_satisfaction_rating}/5)</p>
              </div>
            )}
          </div>
          {maintenance.quality_check_remarks && (
            <div className="mt-3">
              <Label className="text-muted-foreground">Quality Remarks</Label>
              <p className="text-sm mt-1 p-3 bg-muted rounded">{maintenance.quality_check_remarks}</p>
            </div>
          )}
        </div>
      )}
    </div>
  )
}


// Tab 2: Action (Type-specific forms)
function MaintenanceActionTab({ 
  maintenance, 
  onUpdate 
}: { 
  maintenance: MaintenanceRecord
  onUpdate: () => void
}) {
  // Render appropriate form based on maintenance_type
  switch (maintenance.maintenance_type) {
    case MaintenanceType.LOCK_SERVICING:
      return <LockServicingForm maintenance={maintenance} onUpdate={onUpdate} />
    case MaintenanceType.KEY_DUPLICATION:
      return <KeyDuplicationForm maintenance={maintenance} onUpdate={onUpdate} />
    case MaintenanceType.LOCKER_CLEANING:
      return <CleaningForm maintenance={maintenance} onUpdate={onUpdate} />
    case MaintenanceType.VAULT_MAINTENANCE:
      return <VaultMaintenanceForm maintenance={maintenance} onUpdate={onUpdate} />
    case MaintenanceType.FIRE_PROTECTION_CHECK:
      return <FireProtectionCheckForm maintenance={maintenance} onUpdate={onUpdate} />
    case MaintenanceType.LOCK_JAMMING:
      return <ResolveLockJammingForm maintenance={maintenance} onUpdate={onUpdate} />
    case MaintenanceType.KEY_LOST:
      return <HandleLostKeyForm maintenance={maintenance} onUpdate={onUpdate} />
    case MaintenanceType.LOCK_REPLACEMENT:
      return <ReplaceLockForm maintenance={maintenance} onUpdate={onUpdate} />
    case MaintenanceType.MASTER_KEY_REGENERATION:
      return <RegenerateMasterKeyForm maintenance={maintenance} onUpdate={onUpdate} />
    case MaintenanceType.LOCKER_REPAIR:
      return <RepairLockerForm maintenance={maintenance} onUpdate={onUpdate} />
    default:
      return <div className="py-4 text-center text-muted-foreground">Action form not implemented for this maintenance type</div>
  }
}


// Action Form 1: Lock Servicing
function LockServicingForm({ maintenance, onUpdate }: { maintenance: MaintenanceRecord; onUpdate: () => void }) {
  const { toast } = useToast()
  const [formData, setFormData] = useState({
    lock_condition_before: '',
    lubrication_done: false,
    parts_replaced: false,
    replaced_parts_list: [] as string[],
    lock_tested_after_servicing: false,
    lock_condition_after: '',
    action_taken: ''
  })
  
  const performMutation = useMutation({
    mutationFn: (data: any) => maintenanceService.performLockServicing(maintenance.id, data),
    onSuccess: () => {
      toast({ title: 'Success', description: 'Lock servicing completed' })
      onUpdate()
    },
    onError: (error: any) => {
      toast({ title: 'Error', description: error.message, variant: 'destructive' })
    }
  })
  
  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (!formData.lock_condition_before || !formData.lock_condition_after || !formData.action_taken) {
      toast({ title: 'Validation Error', description: 'Please fill all required fields', variant: 'destructive' })
      return
    }
    performMutation.mutate(formData)
  }
  
  return (
    <form onSubmit={handleSubmit} className="space-y-4 py-4">
      <div className="grid grid-cols-2 gap-4">
        <div>
          <Label>Lock Condition Before <span className="text-destructive">*</span></Label>
          <Select value={formData.lock_condition_before} onValueChange={(value) => setFormData({ ...formData, lock_condition_before: value })}>
            <SelectTrigger><SelectValue placeholder="Select condition" /></SelectTrigger>
            <SelectContent>
              <SelectItem value="good">Good</SelectItem>
              <SelectItem value="fair">Fair</SelectItem>
              <SelectItem value="poor">Poor</SelectItem>
            </SelectContent>
          </Select>
        </div>
        
        <div>
          <Label>Lock Condition After <span className="text-destructive">*</span></Label>
          <Select value={formData.lock_condition_after} onValueChange={(value) => setFormData({ ...formData, lock_condition_after: value })}>
            <SelectTrigger><SelectValue placeholder="Select condition" /></SelectTrigger>
            <SelectContent>
              <SelectItem value="excellent">Excellent</SelectItem>
              <SelectItem value="good">Good</SelectItem>
              <SelectItem value="fair">Fair</SelectItem>
            </SelectContent>
          </Select>
        </div>
        
        <div className="flex items-center space-x-2">
          <input
            type="checkbox"
            id="lubrication_done"
            checked={formData.lubrication_done}
            onChange={(e) => setFormData({ ...formData, lubrication_done: e.target.checked })}
            className="rounded border-gray-300"
          />
          <Label htmlFor="lubrication_done" className="cursor-pointer">Lubrication Done</Label>
        </div>
        
        <div className="flex items-center space-x-2">
          <input
            type="checkbox"
            id="lock_tested"
            checked={formData.lock_tested_after_servicing}
            onChange={(e) => setFormData({ ...formData, lock_tested_after_servicing: e.target.checked })}
            className="rounded border-gray-300"
          />
          <Label htmlFor="lock_tested" className="cursor-pointer">Lock Tested After Servicing</Label>
        </div>
        
        <div className="col-span-2 flex items-center space-x-2">
          <input
            type="checkbox"
            id="parts_replaced"
            checked={formData.parts_replaced}
            onChange={(e) => setFormData({ ...formData, parts_replaced: e.target.checked })}
            className="rounded border-gray-300"
          />
          <Label htmlFor="parts_replaced" className="cursor-pointer">Parts Replaced</Label>
        </div>
        
        {formData.parts_replaced && (
          <div className="col-span-2">
            <Label>Replaced Parts List</Label>
            <Textarea
              placeholder="List replaced parts (one per line)"
              value={formData.replaced_parts_list.join('\n')}
              onChange={(e) => setFormData({ ...formData, replaced_parts_list: e.target.value.split('\n').filter(p => p.trim()) })}
              rows={3}
            />
          </div>
        )}
        
        <div className="col-span-2">
          <Label>Action Taken <span className="text-destructive">*</span></Label>
          <Textarea
            placeholder="Describe the servicing actions performed..."
            value={formData.action_taken}
            onChange={(e) => setFormData({ ...formData, action_taken: e.target.value })}
            rows={4}
            required
          />
        </div>
      </div>
      
      <Button type="submit" disabled={performMutation.isPending}>
        {performMutation.isPending ? 'Saving...' : 'Save Servicing Details'}
      </Button>
    </form>
  )
}


// Action Form 2: Key Duplication
function KeyDuplicationForm({ maintenance, onUpdate }: { maintenance: MaintenanceRecord; onUpdate: () => void }) {
  const { toast } = useToast()
  const [formData, setFormData] = useState({
    number_of_keys_duplicated: 1,
    key_type_duplicated: 'customer',
    key_storage_location: '',
    action_taken: ''
  })
  
  const performMutation = useMutation({
    mutationFn: (data: any) => maintenanceService.performKeyDuplication(maintenance.id, data),
    onSuccess: () => {
      toast({ title: 'Success', description: 'Key duplication completed' })
      onUpdate()
    },
    onError: (error: any) => {
      toast({ title: 'Error', description: error.message, variant: 'destructive' })
    }
  })
  
  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (!formData.key_storage_location || !formData.action_taken) {
      toast({ title: 'Validation Error', description: 'Please fill all required fields', variant: 'destructive' })
      return
    }
    performMutation.mutate(formData)
  }
  
  return (
    <form onSubmit={handleSubmit} className="space-y-4 py-4">
      <div className="grid grid-cols-2 gap-4">
        <div>
          <Label>Number of Keys Duplicated <span className="text-destructive">*</span></Label>
          <Input
            type="number"
            min={1}
            max={10}
            value={formData.number_of_keys_duplicated}
            onChange={(e) => setFormData({ ...formData, number_of_keys_duplicated: parseInt(e.target.value) })}
            required
          />
        </div>
        
        <div>
          <Label>Key Type <span className="text-destructive">*</span></Label>
          <Select value={formData.key_type_duplicated} onValueChange={(value) => setFormData({ ...formData, key_type_duplicated: value })}>
            <SelectTrigger><SelectValue /></SelectTrigger>
            <SelectContent>
              <SelectItem value="customer">Customer Key</SelectItem>
              <SelectItem value="bank">Bank Key</SelectItem>
              <SelectItem value="master">Master Key</SelectItem>
            </SelectContent>
          </Select>
        </div>
        
        <div className="col-span-2">
          <Label>Key Storage Location <span className="text-destructive">*</span></Label>
          <Input
            placeholder="e.g., Main vault, Branch safe, Customer locker"
            value={formData.key_storage_location}
            onChange={(e) => setFormData({ ...formData, key_storage_location: e.target.value })}
            required
          />
        </div>
        
        <div className="col-span-2">
          <Label>Action Taken <span className="text-destructive">*</span></Label>
          <Textarea
            placeholder="Describe the key duplication process and details..."
            value={formData.action_taken}
            onChange={(e) => setFormData({ ...formData, action_taken: e.target.value })}
            rows={4}
            required
          />
        </div>
      </div>
      
      <Button type="submit" disabled={performMutation.isPending}>
        {performMutation.isPending ? 'Saving...' : 'Save Key Duplication Details'}
      </Button>
    </form>
  )
}


// Action Form 3: Cleaning
function CleaningForm({ maintenance, onUpdate }: { maintenance: MaintenanceRecord; onUpdate: () => void }) {
  const { toast } = useToast()
  const [formData, setFormData] = useState({
    cleaning_type: CleaningType.ROUTINE,
    areas_cleaned: [] as string[],
    cleaning_materials_used: [] as string[],
    sanitization_done: false,
    action_taken: ''
  })
  
  const performMutation = useMutation({
    mutationFn: (data: any) => maintenanceService.performCleaning(maintenance.id, data),
    onSuccess: () => {
      toast({ title: 'Success', description: 'Cleaning completed' })
      onUpdate()
    },
    onError: (error: any) => {
      toast({ title: 'Error', description: error.message, variant: 'destructive' })
    }
  })
  
  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (formData.areas_cleaned.length === 0 || formData.cleaning_materials_used.length === 0 || !formData.action_taken) {
      toast({ title: 'Validation Error', description: 'Please fill all required fields', variant: 'destructive' })
      return
    }
    performMutation.mutate(formData)
  }
  
  return (
    <form onSubmit={handleSubmit} className="space-y-4 py-4">
      <div className="grid grid-cols-2 gap-4">
        <div>
          <Label>Cleaning Type <span className="text-destructive">*</span></Label>
          <Select value={formData.cleaning_type} onValueChange={(value) => setFormData({ ...formData, cleaning_type: value as CleaningType })}>
            <SelectTrigger><SelectValue /></SelectTrigger>
            <SelectContent>
              <SelectItem value={CleaningType.ROUTINE}>Routine</SelectItem>
              <SelectItem value={CleaningType.DEEP}>Deep Cleaning</SelectItem>
              <SelectItem value={CleaningType.SANITIZATION}>Sanitization</SelectItem>
            </SelectContent>
          </Select>
        </div>
        
        <div className="flex items-center space-x-2">
          <input
            type="checkbox"
            id="sanitization_done"
            checked={formData.sanitization_done}
            onChange={(e) => setFormData({ ...formData, sanitization_done: e.target.checked })}
            className="rounded border-gray-300"
          />
          <Label htmlFor="sanitization_done" className="cursor-pointer">Sanitization Done</Label>
        </div>
        
        <div className="col-span-2">
          <Label>Areas Cleaned <span className="text-destructive">*</span></Label>
          <Textarea
            placeholder="List areas cleaned (one per line): e.g., Locker interior, Lock mechanism, Exterior surface"
            value={formData.areas_cleaned.join('\n')}
            onChange={(e) => setFormData({ ...formData, areas_cleaned: e.target.value.split('\n').filter(a => a.trim()) })}
            rows={3}
          />
        </div>
        
        <div className="col-span-2">
          <Label>Cleaning Materials Used <span className="text-destructive">*</span></Label>
          <Textarea
            placeholder="List materials used (one per line): e.g., Disinfectant spray, Microfiber cloth, Metal polish"
            value={formData.cleaning_materials_used.join('\n')}
            onChange={(e) => setFormData({ ...formData, cleaning_materials_used: e.target.value.split('\n').filter(m => m.trim()) })}
            rows={3}
          />
        </div>
        
        <div className="col-span-2">
          <Label>Action Taken <span className="text-destructive">*</span></Label>
          <Textarea
            placeholder="Describe the cleaning process and observations..."
            value={formData.action_taken}
            onChange={(e) => setFormData({ ...formData, action_taken: e.target.value })}
            rows={4}
            required
          />
        </div>
      </div>
      
      <Button type="submit" disabled={performMutation.isPending}>
        {performMutation.isPending ? 'Saving...' : 'Save Cleaning Details'}
      </Button>
    </form>
  )
}


// Action Form 4: Vault Maintenance
function VaultMaintenanceForm({ maintenance, onUpdate }: { maintenance: MaintenanceRecord; onUpdate: () => void }) {
  const { toast } = useToast()
  const [formData, setFormData] = useState({
    humidity_level_before: undefined as number | undefined,
    humidity_level_after: undefined as number | undefined,
    dehumidifier_checked: false,
    dehumidifier_condition: '',
    ventilation_checked: false,
    action_taken: ''
  })
  
  const performMutation = useMutation({
    mutationFn: (data: any) => maintenanceService.performVaultMaintenance(maintenance.id, data),
    onSuccess: () => {
      toast({ title: 'Success', description: 'Vault maintenance completed' })
      onUpdate()
    },
    onError: (error: any) => {
      toast({ title: 'Error', description: error.message, variant: 'destructive' })
    }
  })
  
  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (!formData.action_taken) {
      toast({ title: 'Validation Error', description: 'Please describe actions taken', variant: 'destructive' })
      return
    }
    performMutation.mutate(formData)
  }
  
  return (
    <form onSubmit={handleSubmit} className="space-y-4 py-4">
      <div className="grid grid-cols-2 gap-4">
        <div>
          <Label>Humidity Level Before (%)</Label>
          <Input
            type="number"
            min={0}
            max={100}
            step={0.1}
            placeholder="e.g., 65.5"
            value={formData.humidity_level_before || ''}
            onChange={(e) => setFormData({ ...formData, humidity_level_before: parseFloat(e.target.value) || undefined })}
          />
        </div>
        
        <div>
          <Label>Humidity Level After (%)</Label>
          <Input
            type="number"
            min={0}
            max={100}
            step={0.1}
            placeholder="e.g., 45.2"
            value={formData.humidity_level_after || ''}
            onChange={(e) => setFormData({ ...formData, humidity_level_after: parseFloat(e.target.value) || undefined })}
          />
        </div>
        
        <div className="flex items-center space-x-2">
          <input
            type="checkbox"
            id="dehumidifier_checked"
            checked={formData.dehumidifier_checked}
            onChange={(e) => setFormData({ ...formData, dehumidifier_checked: e.target.checked })}
            className="rounded border-gray-300"
          />
          <Label htmlFor="dehumidifier_checked" className="cursor-pointer">Dehumidifier Checked</Label>
        </div>
        
        <div className="flex items-center space-x-2">
          <input
            type="checkbox"
            id="ventilation_checked"
            checked={formData.ventilation_checked}
            onChange={(e) => setFormData({ ...formData, ventilation_checked: e.target.checked })}
            className="rounded border-gray-300"
          />
          <Label htmlFor="ventilation_checked" className="cursor-pointer">Ventilation Checked</Label>
        </div>
        
        {formData.dehumidifier_checked && (
          <div className="col-span-2">
            <Label>Dehumidifier Condition</Label>
            <Select value={formData.dehumidifier_condition} onValueChange={(value) => setFormData({ ...formData, dehumidifier_condition: value })}>
              <SelectTrigger><SelectValue placeholder="Select condition" /></SelectTrigger>
              <SelectContent>
                <SelectItem value="good">Good - Working properly</SelectItem>
                <SelectItem value="fair">Fair - Needs minor attention</SelectItem>
                <SelectItem value="poor">Poor - Requires service</SelectItem>
                <SelectItem value="not_working">Not Working - Replacement needed</SelectItem>
              </SelectContent>
            </Select>
          </div>
        )}
        
        <div className="col-span-2">
          <Label>Action Taken <span className="text-destructive">*</span></Label>
          <Textarea
            placeholder="Describe vault maintenance actions, humidity control measures, equipment checks..."
            value={formData.action_taken}
            onChange={(e) => setFormData({ ...formData, action_taken: e.target.value })}
            rows={4}
            required
          />
        </div>
      </div>
      
      <Button type="submit" disabled={performMutation.isPending}>
        {performMutation.isPending ? 'Saving...' : 'Save Vault Maintenance Details'}
      </Button>
    </form>
  )
}


// Action Form 5: Fire Protection Check
function FireProtectionCheckForm({ maintenance, onUpdate }: { maintenance: MaintenanceRecord; onUpdate: () => void }) {
  const { toast } = useToast()
  const [formData, setFormData] = useState({
    fire_extinguisher_checked: false,
    fire_extinguisher_expiry_date: undefined as string | undefined,
    smoke_detector_tested: false,
    smoke_detector_working: false,
    sprinkler_system_tested: false,
    sprinkler_system_working: false,
    action_taken: ''
  })
  
  const performMutation = useMutation({
    mutationFn: (data: any) => maintenanceService.performFireProtectionCheck(maintenance.id, data),
    onSuccess: () => {
      toast({ title: 'Success', description: 'Fire protection check completed' })
      onUpdate()
    },
    onError: (error: any) => {
      toast({ title: 'Error', description: error.message, variant: 'destructive' })
    }
  })
  
  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (!formData.action_taken) {
      toast({ title: 'Validation Error', description: 'Please describe actions taken', variant: 'destructive' })
      return
    }
    performMutation.mutate(formData)
  }
  
  return (
    <form onSubmit={handleSubmit} className="space-y-4 py-4">
      <div className="grid grid-cols-2 gap-4">
        <div className="col-span-2">
          <h4 className="font-semibold mb-2">Fire Extinguisher</h4>
          <div className="flex items-center space-x-2 mb-2">
            <input
              type="checkbox"
              id="extinguisher_checked"
              checked={formData.fire_extinguisher_checked}
              onChange={(e) => setFormData({ ...formData, fire_extinguisher_checked: e.target.checked })}
              className="rounded border-gray-300"
            />
            <Label htmlFor="extinguisher_checked" className="cursor-pointer">Fire Extinguisher Checked</Label>
          </div>
          
          {formData.fire_extinguisher_checked && (
            <div>
              <Label>Expiry Date</Label>
              <Input
                type="date"
                value={formData.fire_extinguisher_expiry_date || ''}
                onChange={(e) => setFormData({ ...formData, fire_extinguisher_expiry_date: e.target.value })}
              />
            </div>
          )}
        </div>
        
        <div className="col-span-2">
          <h4 className="font-semibold mb-2">Smoke Detector</h4>
          <div className="flex items-center space-x-4">
            <div className="flex items-center space-x-2">
              <input
                type="checkbox"
                id="smoke_tested"
                checked={formData.smoke_detector_tested}
                onChange={(e) => setFormData({ ...formData, smoke_detector_tested: e.target.checked })}
                className="rounded border-gray-300"
              />
              <Label htmlFor="smoke_tested" className="cursor-pointer">Tested</Label>
            </div>
            
            {formData.smoke_detector_tested && (
              <div className="flex items-center space-x-2">
                <input
                  type="checkbox"
                  id="smoke_working"
                  checked={formData.smoke_detector_working}
                  onChange={(e) => setFormData({ ...formData, smoke_detector_working: e.target.checked })}
                  className="rounded border-gray-300"
                />
                <Label htmlFor="smoke_working" className="cursor-pointer">Working Properly</Label>
              </div>
            )}
          </div>
        </div>
        
        <div className="col-span-2">
          <h4 className="font-semibold mb-2">Sprinkler System</h4>
          <div className="flex items-center space-x-4">
            <div className="flex items-center space-x-2">
              <input
                type="checkbox"
                id="sprinkler_tested"
                checked={formData.sprinkler_system_tested}
                onChange={(e) => setFormData({ ...formData, sprinkler_system_tested: e.target.checked })}
                className="rounded border-gray-300"
              />
              <Label htmlFor="sprinkler_tested" className="cursor-pointer">Tested</Label>
            </div>
            
            {formData.sprinkler_system_tested && (
              <div className="flex items-center space-x-2">
                <input
                  type="checkbox"
                  id="sprinkler_working"
                  checked={formData.sprinkler_system_working}
                  onChange={(e) => setFormData({ ...formData, sprinkler_system_working: e.target.checked })}
                  className="rounded border-gray-300"
                />
                <Label htmlFor="sprinkler_working" className="cursor-pointer">Working Properly</Label>
              </div>
            )}
          </div>
        </div>
        
        <div className="col-span-2">
          <Label>Action Taken <span className="text-destructive">*</span></Label>
          <Textarea
            placeholder="Describe fire protection checks performed, test results, any issues found..."
            value={formData.action_taken}
            onChange={(e) => setFormData({ ...formData, action_taken: e.target.value })}
            rows={4}
            required
          />
        </div>
      </div>
      
      <Button type="submit" disabled={performMutation.isPending}>
        {performMutation.isPending ? 'Saving...' : 'Save Fire Protection Check Details'}
      </Button>
    </form>
  )
}


// Action Form 6: Resolve Lock Jamming
function ResolveLockJammingForm({ maintenance, onUpdate }: { maintenance: MaintenanceRecord; onUpdate: () => void }) {
  const { toast } = useToast()
  const [formData, setFormData] = useState({
    jamming_cause: LockJammingCause.DUST_ACCUMULATION,
    jamming_resolution_steps: [] as string[],
    lock_repaired: false,
    lock_replaced_due_to_jamming: false,
    action_taken: ''
  })
  
  const performMutation = useMutation({
    mutationFn: (data: any) => maintenanceService.resolveLockJamming(maintenance.id, data),
    onSuccess: () => {
      toast({ title: 'Success', description: 'Lock jamming resolved' })
      onUpdate()
    },
    onError: (error: any) => {
      toast({ title: 'Error', description: error.message, variant: 'destructive' })
    }
  })
  
  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (formData.jamming_resolution_steps.length === 0 || !formData.action_taken) {
      toast({ title: 'Validation Error', description: 'Please fill all required fields', variant: 'destructive' })
      return
    }
    performMutation.mutate(formData)
  }
  
  return (
    <form onSubmit={handleSubmit} className="space-y-4 py-4">
      <div className="grid grid-cols-2 gap-4">
        <div className="col-span-2">
          <Label>Jamming Cause <span className="text-destructive">*</span></Label>
          <Select value={formData.jamming_cause} onValueChange={(value) => setFormData({ ...formData, jamming_cause: value as LockJammingCause })}>
            <SelectTrigger><SelectValue /></SelectTrigger>
            <SelectContent>
              <SelectItem value={LockJammingCause.DUST_ACCUMULATION}>Dust Accumulation</SelectItem>
              <SelectItem value={LockJammingCause.LACK_OF_LUBRICATION}>Lack of Lubrication</SelectItem>
              <SelectItem value={LockJammingCause.WORN_OUT_PARTS}>Worn Out Parts</SelectItem>
              <SelectItem value={LockJammingCause.FOREIGN_OBJECT}>Foreign Object</SelectItem>
              <SelectItem value={LockJammingCause.MISALIGNMENT}>Misalignment</SelectItem>
              <SelectItem value={LockJammingCause.OTHER}>Other</SelectItem>
            </SelectContent>
          </Select>
        </div>
        
        <div className="col-span-2">
          <Label>Resolution Steps <span className="text-destructive">*</span></Label>
          <Textarea
            placeholder="List steps taken to resolve jamming (one per line):&#10;1. Cleaned lock mechanism&#10;2. Applied lubricant&#10;3. Tested key operation"
            value={formData.jamming_resolution_steps.join('\n')}
            onChange={(e) => setFormData({ ...formData, jamming_resolution_steps: e.target.value.split('\n').filter(s => s.trim()) })}
            rows={5}
          />
        </div>
        
        <div className="flex items-center space-x-2">
          <input
            type="checkbox"
            id="lock_repaired"
            checked={formData.lock_repaired}
            onChange={(e) => setFormData({ ...formData, lock_repaired: e.target.checked })}
            className="rounded border-gray-300"
          />
          <Label htmlFor="lock_repaired" className="cursor-pointer">Lock Repaired</Label>
        </div>
        
        <div className="flex items-center space-x-2">
          <input
            type="checkbox"
            id="lock_replaced"
            checked={formData.lock_replaced_due_to_jamming}
            onChange={(e) => setFormData({ ...formData, lock_replaced_due_to_jamming: e.target.checked })}
            className="rounded border-gray-300"
          />
          <Label htmlFor="lock_replaced" className="cursor-pointer">Lock Replaced</Label>
        </div>
        
        <div className="col-span-2">
          <Label>Action Taken <span className="text-destructive">*</span></Label>
          <Textarea
            placeholder="Describe detailed actions taken to resolve the lock jamming issue..."
            value={formData.action_taken}
            onChange={(e) => setFormData({ ...formData, action_taken: e.target.value })}
            rows={4}
            required
          />
        </div>
      </div>
      
      <Button type="submit" disabled={performMutation.isPending}>
        {performMutation.isPending ? 'Saving...' : 'Save Resolution Details'}
      </Button>
    </form>
  )
}


// Action Form 7: Handle Lost Key
function HandleLostKeyForm({ maintenance, onUpdate }: { maintenance: MaintenanceRecord; onUpdate: () => void }) {
  const { toast } = useToast()
  const [formData, setFormData] = useState({
    fir_details: '',
    indemnity_bond_collected: false,
    indemnity_bond_path: '',
    key_replacement_action: KeyReplacementAction.DUPLICATE_KEY,
    new_key_number: '',
    customer_charge_amount: 0,
    action_taken: ''
  })
  
  const performMutation = useMutation({
    mutationFn: (data: any) => maintenanceService.handleLostKey(maintenance.id, data),
    onSuccess: () => {
      toast({ title: 'Success', description: 'Lost key handled' })
      onUpdate()
    },
    onError: (error: any) => {
      toast({ title: 'Error', description: error.message, variant: 'destructive' })
    }
  })
  
  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (!formData.fir_details || !formData.action_taken) {
      toast({ title: 'Validation Error', description: 'FIR details and action taken are required', variant: 'destructive' })
      return
    }
    if (formData.indemnity_bond_collected && !formData.indemnity_bond_path) {
      toast({ title: 'Validation Error', description: 'Please upload indemnity bond document', variant: 'destructive' })
      return
    }
    performMutation.mutate(formData)
  }
  
  return (
    <form onSubmit={handleSubmit} className="space-y-4 py-4">
      <div className="grid grid-cols-2 gap-4">
        <div className="col-span-2">
          <Label>FIR Details <span className="text-destructive">*</span></Label>
          <Input
            placeholder="FIR Number and Police Station"
            value={formData.fir_details}
            onChange={(e) => setFormData({ ...formData, fir_details: e.target.value })}
            required
          />
        </div>
        
        <div className="col-span-2 flex items-center space-x-2">
          <input
            type="checkbox"
            id="indemnity_collected"
            checked={formData.indemnity_bond_collected}
            onChange={(e) => setFormData({ ...formData, indemnity_bond_collected: e.target.checked })}
            className="rounded border-gray-300"
          />
          <Label htmlFor="indemnity_collected" className="cursor-pointer">Indemnity Bond Collected</Label>
        </div>
        
        {formData.indemnity_bond_collected && (
          <div className="col-span-2">
            <Label>Indemnity Bond Document <span className="text-destructive">*</span></Label>
            <Input
              type="file"
              accept=".pdf,.jpg,.jpeg,.png"
              onChange={(e) => {
                const file = e.target.files?.[0]
                if (file) {
                  // In real implementation, upload to server and get path
                  setFormData({ ...formData, indemnity_bond_path: `uploads/indemnity/${file.name}` })
                  toast({ title: 'File Selected', description: file.name })
                }
              }}
            />
            <p className="text-xs text-muted-foreground mt-1">Upload PDF, JPG, or PNG (Max 5MB)</p>
          </div>
        )}
        
        <div className="col-span-2">
          <Label>Key Replacement Action <span className="text-destructive">*</span></Label>
          <Select value={formData.key_replacement_action} onValueChange={(value) => setFormData({ ...formData, key_replacement_action: value as KeyReplacementAction })}>
            <SelectTrigger><SelectValue /></SelectTrigger>
            <SelectContent>
              <SelectItem value={KeyReplacementAction.DUPLICATE_KEY}>Duplicate Existing Key</SelectItem>
              <SelectItem value={KeyReplacementAction.REPLACE_LOCK}>Replace Entire Lock</SelectItem>
              <SelectItem value={KeyReplacementAction.MASTER_KEY_ACCESS}>Provide Master Key Access</SelectItem>
              <SelectItem value={KeyReplacementAction.NO_ACTION}>No Action (Investigation pending)</SelectItem>
            </SelectContent>
          </Select>
        </div>
        
        {formData.key_replacement_action !== KeyReplacementAction.NO_ACTION && (
          <div className="col-span-2">
            <Label>New Key Number</Label>
            <Input
              placeholder="e.g., KEY-2024-001234"
              value={formData.new_key_number}
              onChange={(e) => setFormData({ ...formData, new_key_number: e.target.value })}
            />
          </div>
        )}
        
        <div className="col-span-2">
          <Label>Customer Charge Amount (₹)</Label>
          <Input
            type="number"
            min={0}
            step={0.01}
            placeholder="e.g., 5000"
            value={formData.customer_charge_amount}
            onChange={(e) => setFormData({ ...formData, customer_charge_amount: parseFloat(e.target.value) || 0 })}
          />
          <p className="text-xs text-muted-foreground mt-1">Charges for key replacement, lock change, etc. (GST will be added)</p>
        </div>
        
        <div className="col-span-2">
          <Label>Action Taken <span className="text-destructive">*</span></Label>
          <Textarea
            placeholder="Describe the complete process: FIR verification, indemnity bond collection, key replacement steps..."
            value={formData.action_taken}
            onChange={(e) => setFormData({ ...formData, action_taken: e.target.value })}
            rows={5}
            required
          />
        </div>
      </div>
      
      <Button type="submit" disabled={performMutation.isPending}>
        {performMutation.isPending ? 'Saving...' : 'Save Lost Key Details'}
      </Button>
    </form>
  )
}


// Action Form 8: Replace Lock
function ReplaceLockForm({ maintenance, onUpdate }: { maintenance: MaintenanceRecord; onUpdate: () => void }) {
  const { toast } = useToast()
  const [formData, setFormData] = useState({
    old_lock_number: '',
    old_lock_condition: '',
    new_lock_number: '',
    new_lock_type: '',
    lock_installation_date: new Date().toISOString().split('T')[0],
    keys_issued_count: 2,
    customer_notified_of_replacement: false,
    action_taken: ''
  })
  
  const performMutation = useMutation({
    mutationFn: (data: any) => maintenanceService.replaceLock(maintenance.id, data),
    onSuccess: () => {
      toast({ title: 'Success', description: 'Lock replaced successfully' })
      onUpdate()
    },
    onError: (error: any) => {
      toast({ title: 'Error', description: error.message, variant: 'destructive' })
    }
  })
  
  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (!formData.old_lock_number || !formData.new_lock_number || !formData.new_lock_type || !formData.action_taken) {
      toast({ title: 'Validation Error', description: 'Please fill all required fields', variant: 'destructive' })
      return
    }
    performMutation.mutate(formData)
  }
  
  return (
    <form onSubmit={handleSubmit} className="space-y-4 py-4">
      <div className="grid grid-cols-2 gap-4">
        <div className="col-span-2">
          <h4 className="font-semibold mb-2">Old Lock Details</h4>
        </div>
        
        <div>
          <Label>Old Lock Number <span className="text-destructive">*</span></Label>
          <Input
            placeholder="e.g., LOCK-2020-001"
            value={formData.old_lock_number}
            onChange={(e) => setFormData({ ...formData, old_lock_number: e.target.value })}
            required
          />
        </div>
        
        <div>
          <Label>Old Lock Condition <span className="text-destructive">*</span></Label>
          <Select value={formData.old_lock_condition} onValueChange={(value) => setFormData({ ...formData, old_lock_condition: value })}>
            <SelectTrigger><SelectValue placeholder="Select condition" /></SelectTrigger>
            <SelectContent>
              <SelectItem value="damaged">Damaged - Beyond repair</SelectItem>
              <SelectItem value="worn_out">Worn Out - End of life</SelectItem>
              <SelectItem value="compromised">Compromised - Security issue</SelectItem>
              <SelectItem value="obsolete">Obsolete - Outdated model</SelectItem>
            </SelectContent>
          </Select>
        </div>
        
        <div className="col-span-2">
          <h4 className="font-semibold mb-2 mt-2">New Lock Details</h4>
        </div>
        
        <div>
          <Label>New Lock Number <span className="text-destructive">*</span></Label>
          <Input
            placeholder="e.g., LOCK-2024-501"
            value={formData.new_lock_number}
            onChange={(e) => setFormData({ ...formData, new_lock_number: e.target.value })}
            required
          />
        </div>
        
        <div>
          <Label>New Lock Type <span className="text-destructive">*</span></Label>
          <Input
            placeholder="e.g., Yale Triple Lock, Godrej 7-Lever"
            value={formData.new_lock_type}
            onChange={(e) => setFormData({ ...formData, new_lock_type: e.target.value })}
            required
          />
        </div>
        
        <div>
          <Label>Installation Date <span className="text-destructive">*</span></Label>
          <Input
            type="date"
            value={formData.lock_installation_date}
            onChange={(e) => setFormData({ ...formData, lock_installation_date: e.target.value })}
            required
          />
        </div>
        
        <div>
          <Label>Number of Keys Issued <span className="text-destructive">*</span></Label>
          <Input
            type="number"
            min={2}
            max={10}
            value={formData.keys_issued_count}
            onChange={(e) => setFormData({ ...formData, keys_issued_count: parseInt(e.target.value) })}
            required
          />
        </div>
        
        <div className="col-span-2 flex items-center space-x-2">
          <input
            type="checkbox"
            id="customer_notified"
            checked={formData.customer_notified_of_replacement}
            onChange={(e) => setFormData({ ...formData, customer_notified_of_replacement: e.target.checked })}
            className="rounded border-gray-300"
          />
          <Label htmlFor="customer_notified" className="cursor-pointer">Customer Notified of Replacement</Label>
        </div>
        
        <div className="col-span-2">
          <Label>Action Taken <span className="text-destructive">*</span></Label>
          <Textarea
            placeholder="Describe lock replacement process: removal, installation, testing, key handover..."
            value={formData.action_taken}
            onChange={(e) => setFormData({ ...formData, action_taken: e.target.value })}
            rows={5}
            required
          />
        </div>
      </div>
      
      <Button type="submit" disabled={performMutation.isPending}>
        {performMutation.isPending ? 'Saving...' : 'Save Lock Replacement Details'}
      </Button>
    </form>
  )
}


// Action Form 9: Regenerate Master Key
function RegenerateMasterKeyForm({ maintenance, onUpdate }: { maintenance: MaintenanceRecord; onUpdate: () => void }) {
  const { toast } = useToast()
  const [formData, setFormData] = useState({
    authorization_for_regeneration: '',
    new_master_key_number: '',
    all_affected_lockers: [] as string[],
    customer_keys_retained: false,
    action_taken: ''
  })
  
  const performMutation = useMutation({
    mutationFn: (data: any) => maintenanceService.regenerateMasterKey(maintenance.id, data),
    onSuccess: () => {
      toast({ title: 'Success', description: 'Master key regenerated' })
      onUpdate()
    },
    onError: (error: any) => {
      toast({ title: 'Error', description: error.message, variant: 'destructive' })
    }
  })
  
  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (!formData.authorization_for_regeneration || !formData.new_master_key_number || formData.all_affected_lockers.length === 0 || !formData.action_taken) {
      toast({ title: 'Validation Error', description: 'Please fill all required fields', variant: 'destructive' })
      return
    }
    performMutation.mutate(formData)
  }
  
  return (
    <form onSubmit={handleSubmit} className="space-y-4 py-4">
      <div className="space-y-4">
        <div className="p-3 bg-yellow-50 border border-yellow-200 rounded">
          <p className="text-sm text-yellow-800 font-medium">⚠️ Security Critical Operation</p>
          <p className="text-xs text-yellow-700 mt-1">Master key regeneration affects all lockers in the vault. Requires management authorization.</p>
        </div>
        
        <div>
          <Label>Authorization Details <span className="text-destructive">*</span></Label>
          <Input
            placeholder="Authorization letter number or approval reference"
            value={formData.authorization_for_regeneration}
            onChange={(e) => setFormData({ ...formData, authorization_for_regeneration: e.target.value })}
            required
          />
        </div>
        
        <div>
          <Label>New Master Key Number <span className="text-destructive">*</span></Label>
          <Input
            placeholder="e.g., MASTER-KEY-2024-V2"
            value={formData.new_master_key_number}
            onChange={(e) => setFormData({ ...formData, new_master_key_number: e.target.value })}
            required
          />
        </div>
        
        <div>
          <Label>Affected Lockers <span className="text-destructive">*</span></Label>
          <Textarea
            placeholder="List all locker IDs affected by master key regeneration (one per line):&#10;LOCKER-001&#10;LOCKER-002&#10;LOCKER-003"
            value={formData.all_affected_lockers.join('\n')}
            onChange={(e) => setFormData({ ...formData, all_affected_lockers: e.target.value.split('\n').filter(l => l.trim()) })}
            rows={6}
          />
          <p className="text-xs text-muted-foreground mt-1">{formData.all_affected_lockers.length} locker(s) affected</p>
        </div>
        
        <div className="flex items-center space-x-2">
          <input
            type="checkbox"
            id="customer_keys_retained"
            checked={formData.customer_keys_retained}
            onChange={(e) => setFormData({ ...formData, customer_keys_retained: e.target.checked })}
            className="rounded border-gray-300"
          />
          <Label htmlFor="customer_keys_retained" className="cursor-pointer">Customer Keys Retained (No new keys issued to customers)</Label>
        </div>
        
        <div>
          <Label>Action Taken <span className="text-destructive">*</span></Label>
          <Textarea
            placeholder="Describe master key regeneration process: authorization verification, key generation, testing, affected locker updates, security measures..."
            value={formData.action_taken}
            onChange={(e) => setFormData({ ...formData, action_taken: e.target.value })}
            rows={6}
            required
          />
        </div>
      </div>
      
      <Button type="submit" disabled={performMutation.isPending} variant="destructive">
        {performMutation.isPending ? 'Processing...' : 'Confirm Master Key Regeneration'}
      </Button>
    </form>
  )
}


// Action Form 10: Repair Locker
function RepairLockerForm({ maintenance, onUpdate }: { maintenance: MaintenanceRecord; onUpdate: () => void }) {
  const { toast } = useToast()
  const [formData, setFormData] = useState({
    damage_type: '',
    damage_description: '',
    repair_materials_used: [] as string[],
    customer_charged: false,
    customer_charge_reason: '',
    customer_charge_amount: 0,
    action_taken: ''
  })
  
  const performMutation = useMutation({
    mutationFn: (data: any) => maintenanceService.repairLocker(maintenance.id, data),
    onSuccess: () => {
      toast({ title: 'Success', description: 'Locker repair completed' })
      onUpdate()
    },
    onError: (error: any) => {
      toast({ title: 'Error', description: error.message, variant: 'destructive' })
    }
  })
  
  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (!formData.damage_type || !formData.damage_description || formData.repair_materials_used.length === 0 || !formData.action_taken) {
      toast({ title: 'Validation Error', description: 'Please fill all required fields', variant: 'destructive' })
      return
    }
    if (formData.customer_charged && (!formData.customer_charge_reason || formData.customer_charge_amount <= 0)) {
      toast({ title: 'Validation Error', description: 'Please provide charge reason and amount', variant: 'destructive' })
      return
    }
    performMutation.mutate(formData)
  }
  
  return (
    <form onSubmit={handleSubmit} className="space-y-4 py-4">
      <div className="grid grid-cols-2 gap-4">
        <div className="col-span-2">
          <Label>Damage Type <span className="text-destructive">*</span></Label>
          <Select value={formData.damage_type} onValueChange={(value) => setFormData({ ...formData, damage_type: value })}>
            <SelectTrigger><SelectValue placeholder="Select damage type" /></SelectTrigger>
            <SelectContent>
              <SelectItem value="physical_damage">Physical Damage (Dents, Scratches)</SelectItem>
              <SelectItem value="door_misalignment">Door Misalignment</SelectItem>
              <SelectItem value="hinge_damage">Hinge Damage</SelectItem>
              <SelectItem value="rust_corrosion">Rust / Corrosion</SelectItem>
              <SelectItem value="paint_peeling">Paint Peeling</SelectItem>
              <SelectItem value="structural_damage">Structural Damage</SelectItem>
              <SelectItem value="other">Other</SelectItem>
            </SelectContent>
          </Select>
        </div>
        
        <div className="col-span-2">
          <Label>Damage Description <span className="text-destructive">*</span></Label>
          <Textarea
            placeholder="Describe the damage in detail: location, extent, cause (if known)..."
            value={formData.damage_description}
            onChange={(e) => setFormData({ ...formData, damage_description: e.target.value })}
            rows={4}
            required
          />
        </div>
        
        <div className="col-span-2">
          <Label>Repair Materials Used <span className="text-destructive">*</span></Label>
          <Textarea
            placeholder="List materials used for repair (one per line):&#10;Welding rod&#10;Metal primer&#10;Touch-up paint"
            value={formData.repair_materials_used.join('\n')}
            onChange={(e) => setFormData({ ...formData, repair_materials_used: e.target.value.split('\n').filter(m => m.trim()) })}
            rows={4}
          />
        </div>
        
        <div className="col-span-2">
          <h4 className="font-semibold mb-2">Photo Documentation</h4>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <Label>Before Repair Photos</Label>
              <Input
                type="file"
                accept="image/*"
                multiple
                onChange={(e) => {
                  const files = Array.from(e.target.files || [])
                  if (files.length > 0) {
                    toast({ title: 'Photos Selected', description: `${files.length} before photos selected` })
                  }
                }}
              />
            </div>
            <div>
              <Label>After Repair Photos</Label>
              <Input
                type="file"
                accept="image/*"
                multiple
                onChange={(e) => {
                  const files = Array.from(e.target.files || [])
                  if (files.length > 0) {
                    toast({ title: 'Photos Selected', description: `${files.length} after photos selected` })
                  }
                }}
              />
            </div>
          </div>
          <p className="text-xs text-muted-foreground mt-1">Upload multiple photos showing damage and repair work</p>
        </div>
        
        <div className="col-span-2">
          <h4 className="font-semibold mb-2">Customer Charges</h4>
          <div className="flex items-center space-x-2 mb-3">
            <input
              type="checkbox"
              id="customer_charged"
              checked={formData.customer_charged}
              onChange={(e) => setFormData({ ...formData, customer_charged: e.target.checked })}
              className="rounded border-gray-300"
            />
            <Label htmlFor="customer_charged" className="cursor-pointer">Charge Customer for Repair</Label>
          </div>
          
          {formData.customer_charged && (
            <div className="grid grid-cols-2 gap-4">
              <div>
                <Label>Charge Reason <span className="text-destructive">*</span></Label>
                <Input
                  placeholder="e.g., Customer-induced damage, Misuse"
                  value={formData.customer_charge_reason}
                  onChange={(e) => setFormData({ ...formData, customer_charge_reason: e.target.value })}
                  required
                />
              </div>
              <div>
                <Label>Charge Amount (₹) <span className="text-destructive">*</span></Label>
                <Input
                  type="number"
                  min={0}
                  step={0.01}
                  placeholder="e.g., 2500"
                  value={formData.customer_charge_amount}
                  onChange={(e) => setFormData({ ...formData, customer_charge_amount: parseFloat(e.target.value) || 0 })}
                  required
                />
              </div>
            </div>
          )}
        </div>
        
        <div className="col-span-2">
          <Label>Action Taken <span className="text-destructive">*</span></Label>
          <Textarea
            placeholder="Describe complete repair process: assessment, repair steps, testing, quality check..."
            value={formData.action_taken}
            onChange={(e) => setFormData({ ...formData, action_taken: e.target.value })}
            rows={5}
            required
          />
        </div>
      </div>
      
      <Button type="submit" disabled={performMutation.isPending}>
        {performMutation.isPending ? 'Saving...' : 'Save Repair Details'}
      </Button>
    </form>
  )
}


// Tab 3: Cost Management
function MaintenanceCostTab({ 
  maintenance, 
  onUpdate 
}: { 
  maintenance: MaintenanceRecord
  onUpdate: () => void
}) {
  const { toast } = useToast()
  const [isEditing, setIsEditing] = useState(false)
  const [formData, setFormData] = useState({
    labor_cost: maintenance.labor_cost || 0,
    material_cost: maintenance.material_cost || 0,
    external_service_cost: maintenance.external_service_cost || 0,
    customer_charged: maintenance.customer_charged || false,
    customer_charge_reason: maintenance.customer_charge_reason || '',
    customer_charge_amount: maintenance.customer_charge_amount || 0
  })
  
  // Calculate totals
  const totalMaintenanceCost = formData.labor_cost + formData.material_cost + formData.external_service_cost
  const customerGST = formData.customer_charged ? formData.customer_charge_amount * 0.18 : 0
  const customerTotalCharge = formData.customer_charged ? formData.customer_charge_amount + customerGST : 0
  
  const updateCostMutation = useMutation({
    mutationFn: (data: any) => maintenanceService.updateMaintenanceCost(maintenance.id, {
      ...data,
      total_maintenance_cost: totalMaintenanceCost,
      customer_charge_gst_amount: customerGST,
      customer_total_charge: customerTotalCharge
    }),
    onSuccess: () => {
      toast({ title: 'Success', description: 'Cost details updated' })
      setIsEditing(false)
      onUpdate()
    },
    onError: (error: any) => {
      toast({ title: 'Error', description: error.message, variant: 'destructive' })
    }
  })
  
  const handleSave = () => {
    if (formData.customer_charged && (!formData.customer_charge_reason || formData.customer_charge_amount <= 0)) {
      toast({ 
        title: 'Validation Error', 
        description: 'Please provide customer charge reason and amount', 
        variant: 'destructive' 
      })
      return
    }
    updateCostMutation.mutate(formData)
  }
  
  const isCompleted = maintenance.status === 'completed'
  
  return (
    <div className="space-y-6 py-4">
      {/* Maintenance Costs */}
      <div>
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold">Maintenance Costs</h3>
          {!isCompleted && (
            <Button 
              variant={isEditing ? 'outline' : 'default'} 
              size="sm"
              onClick={() => setIsEditing(!isEditing)}
            >
              {isEditing ? 'Cancel' : 'Edit Costs'}
            </Button>
          )}
        </div>
        
        <div className="grid grid-cols-3 gap-4">
          <div>
            <Label>Labor Cost (₹)</Label>
            {isEditing ? (
              <Input
                type="number"
                min={0}
                step={0.01}
                value={formData.labor_cost}
                onChange={(e) => setFormData({ ...formData, labor_cost: parseFloat(e.target.value) || 0 })}
              />
            ) : (
              <p className="font-medium text-lg mt-2">{formatCurrency(formData.labor_cost)}</p>
            )}
          </div>
          
          <div>
            <Label>Material Cost (₹)</Label>
            {isEditing ? (
              <Input
                type="number"
                min={0}
                step={0.01}
                value={formData.material_cost}
                onChange={(e) => setFormData({ ...formData, material_cost: parseFloat(e.target.value) || 0 })}
              />
            ) : (
              <p className="font-medium text-lg mt-2">{formatCurrency(formData.material_cost)}</p>
            )}
          </div>
          
          <div>
            <Label>External Service Cost (₹)</Label>
            {isEditing ? (
              <Input
                type="number"
                min={0}
                step={0.01}
                value={formData.external_service_cost}
                onChange={(e) => setFormData({ ...formData, external_service_cost: parseFloat(e.target.value) || 0 })}
              />
            ) : (
              <p className="font-medium text-lg mt-2">{formatCurrency(formData.external_service_cost)}</p>
            )}
          </div>
        </div>
        
        <div className="mt-4 pt-4 border-t">
          <div className="flex items-center justify-between">
            <Label className="text-lg">Total Maintenance Cost</Label>
            <p className="font-bold text-2xl">{formatCurrency(totalMaintenanceCost)}</p>
          </div>
        </div>
      </div>
      
      {/* Customer Charges */}
      <div className="pt-4 border-t">
        <h3 className="text-lg font-semibold mb-4">Customer Charges</h3>
        
        {isEditing ? (
          <div className="space-y-4">
            <div className="flex items-center space-x-2">
              <input
                type="checkbox"
                id="customer_charged_edit"
                checked={formData.customer_charged}
                onChange={(e) => setFormData({ ...formData, customer_charged: e.target.checked })}
                className="rounded border-gray-300"
              />
              <Label htmlFor="customer_charged_edit" className="cursor-pointer">
                Charge Customer for Maintenance
              </Label>
            </div>
            
            {formData.customer_charged && (
              <div className="grid grid-cols-2 gap-4 p-4 bg-orange-50 border border-orange-200 rounded">
                <div className="col-span-2">
                  <Label>Charge Reason <span className="text-destructive">*</span></Label>
                  <Input
                    placeholder="e.g., Customer fault, Misuse, Lost key charges"
                    value={formData.customer_charge_reason}
                    onChange={(e) => setFormData({ ...formData, customer_charge_reason: e.target.value })}
                    required
                  />
                </div>
                
                <div>
                  <Label>Base Amount (₹) <span className="text-destructive">*</span></Label>
                  <Input
                    type="number"
                    min={0}
                    step={0.01}
                    placeholder="e.g., 5000"
                    value={formData.customer_charge_amount}
                    onChange={(e) => setFormData({ ...formData, customer_charge_amount: parseFloat(e.target.value) || 0 })}
                    required
                  />
                </div>
                
                <div>
                  <Label>GST @ 18%</Label>
                  <p className="font-medium text-lg mt-2">{formatCurrency(customerGST)}</p>
                </div>
                
                <div className="col-span-2 pt-3 border-t border-orange-300">
                  <div className="flex items-center justify-between">
                    <Label className="text-lg">Total Customer Charge</Label>
                    <p className="font-bold text-2xl text-orange-600">{formatCurrency(customerTotalCharge)}</p>
                  </div>
                </div>
              </div>
            )}
          </div>
        ) : (
          <div>
            {formData.customer_charged ? (
              <div className="p-4 bg-orange-50 border border-orange-200 rounded">
                <div className="grid grid-cols-3 gap-4">
                  <div>
                    <Label className="text-muted-foreground">Base Amount</Label>
                    <p className="font-medium text-lg">{formatCurrency(formData.customer_charge_amount)}</p>
                  </div>
                  <div>
                    <Label className="text-muted-foreground">GST @ 18%</Label>
                    <p className="font-medium text-lg">{formatCurrency(customerGST)}</p>
                  </div>
                  <div>
                    <Label className="text-muted-foreground">Total Charge</Label>
                    <p className="font-bold text-xl text-orange-600">{formatCurrency(customerTotalCharge)}</p>
                  </div>
                  
                  {formData.customer_charge_reason && (
                    <div className="col-span-3 pt-3 border-t border-orange-300">
                      <Label className="text-muted-foreground">Charge Reason</Label>
                      <p className="text-sm mt-1">{formData.customer_charge_reason}</p>
                    </div>
                  )}
                </div>
              </div>
            ) : (
              <p className="text-muted-foreground py-4 text-center border rounded">
                No customer charges applied for this maintenance
              </p>
            )}
          </div>
        )}
      </div>
      
      {/* Cost Breakdown Summary */}
      <div className="pt-4 border-t">
        <h3 className="text-lg font-semibold mb-4">Cost Summary</h3>
        <div className="grid grid-cols-2 gap-4 p-4 bg-muted rounded">
          <div>
            <Label className="text-muted-foreground">Bank's Total Cost</Label>
            <p className="font-bold text-xl">{formatCurrency(totalMaintenanceCost)}</p>
            <p className="text-xs text-muted-foreground mt-1">Labor + Material + External Service</p>
          </div>
          <div>
            <Label className="text-muted-foreground">Recovered from Customer</Label>
            <p className="font-bold text-xl text-green-600">{formatCurrency(customerTotalCharge)}</p>
            <p className="text-xs text-muted-foreground mt-1">Customer charges with GST</p>
          </div>
          <div className="col-span-2 pt-3 border-t">
            <Label className="text-muted-foreground">Net Cost to Bank</Label>
            <p className="font-bold text-2xl">{formatCurrency(totalMaintenanceCost - customerTotalCharge)}</p>
          </div>
        </div>
      </div>
      
      {isEditing && (
        <div className="flex gap-2">
          <Button onClick={handleSave} disabled={updateCostMutation.isPending}>
            {updateCostMutation.isPending ? 'Saving...' : 'Save Cost Details'}
          </Button>
          <Button variant="outline" onClick={() => {
            setIsEditing(false)
            setFormData({
              labor_cost: maintenance.labor_cost || 0,
              material_cost: maintenance.material_cost || 0,
              external_service_cost: maintenance.external_service_cost || 0,
              customer_charged: maintenance.customer_charged || false,
              customer_charge_reason: maintenance.customer_charge_reason || '',
              customer_charge_amount: maintenance.customer_charge_amount || 0
            })
          }}>
            Reset
          </Button>
        </div>
      )}
    </div>
  )
}


// Tab 4: Completion & Quality Check
function MaintenanceCompletionTab({ 
  maintenance, 
  onUpdate,
  onClose
}: { 
  maintenance: MaintenanceRecord
  onUpdate: () => void
  onClose: () => void
}) {
  const { toast } = useToast()
  const [formData, setFormData] = useState({
    completed_date: new Date().toISOString().split('T')[0],
    quality_check_done: false,
    quality_check_by: '',
    quality_check_passed: false,
    quality_check_remarks: '',
    customer_satisfaction_rating: 0,
    customer_satisfaction_feedback: '',
    recommendations: ''
  })
  
  const completeMutation = useMutation({
    mutationFn: (data: any) => maintenanceService.completeMaintenance(maintenance.id, data),
    onSuccess: () => {
      toast({ 
        title: 'Success', 
        description: 'Maintenance completed successfully',
        duration: 3000
      })
      onUpdate()
      onClose()
    },
    onError: (error: any) => {
      toast({ 
        title: 'Error', 
        description: error.message, 
        variant: 'destructive' 
      })
    }
  })
  
  const handleComplete = (e: React.FormEvent) => {
    e.preventDefault()
    
    // Validation
    if (!formData.completed_date) {
      toast({ 
        title: 'Validation Error', 
        description: 'Completion date is required', 
        variant: 'destructive' 
      })
      return
    }
    
    if (formData.quality_check_done) {
      if (!formData.quality_check_by || formData.quality_check_remarks === '') {
        toast({ 
          title: 'Validation Error', 
          description: 'Quality check details are required when quality check is done', 
          variant: 'destructive' 
        })
        return
      }
    }
    
    // Confirmation for completion
    const confirmed = confirm(
      `Complete this maintenance?\n\n` +
      `Maintenance: ${maintenance.maintenance_number}\n` +
      `Type: ${maintenance.maintenance_type}\n` +
      `Quality Check: ${formData.quality_check_done ? (formData.quality_check_passed ? 'PASSED' : 'FAILED') : 'Not performed'}\n\n` +
      `This action cannot be undone.`
    )
    
    if (!confirmed) return
    
    completeMutation.mutate(formData)
  }
  
  return (
    <form onSubmit={handleComplete} className="space-y-6 py-4">
      {/* Completion Information */}
      <div>
        <h3 className="text-lg font-semibold mb-4">Completion Information</h3>
        <div className="grid grid-cols-2 gap-4">
          <div>
            <Label>Completion Date <span className="text-destructive">*</span></Label>
            <Input
              type="date"
              value={formData.completed_date}
              onChange={(e) => setFormData({ ...formData, completed_date: e.target.value })}
              max={new Date().toISOString().split('T')[0]}
              required
            />
          </div>
        </div>
      </div>
      
      {/* Quality Check */}
      <div className="pt-4 border-t">
        <h3 className="text-lg font-semibold mb-4">Quality Check</h3>
        
        <div className="flex items-center space-x-2 mb-4">
          <input
            type="checkbox"
            id="quality_check_done"
            checked={formData.quality_check_done}
            onChange={(e) => setFormData({ ...formData, quality_check_done: e.target.checked })}
            className="rounded border-gray-300"
          />
          <Label htmlFor="quality_check_done" className="cursor-pointer">
            Quality Check Performed
          </Label>
        </div>
        
        {formData.quality_check_done && (
          <div className="space-y-4 p-4 bg-blue-50 border border-blue-200 rounded">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <Label>Quality Check By <span className="text-destructive">*</span></Label>
                <Input
                  placeholder="Supervisor name or ID"
                  value={formData.quality_check_by}
                  onChange={(e) => setFormData({ ...formData, quality_check_by: e.target.value })}
                  required
                />
              </div>
              
              <div className="flex items-center space-x-2">
                <input
                  type="checkbox"
                  id="quality_check_passed"
                  checked={formData.quality_check_passed}
                  onChange={(e) => setFormData({ ...formData, quality_check_passed: e.target.checked })}
                  className="rounded border-gray-300"
                />
                <Label htmlFor="quality_check_passed" className="cursor-pointer font-medium">
                  Quality Check PASSED ✓
                </Label>
              </div>
            </div>
            
            <div>
              <Label>Quality Check Remarks <span className="text-destructive">*</span></Label>
              <Textarea
                placeholder="Quality check observations, test results, compliance verification..."
                value={formData.quality_check_remarks}
                onChange={(e) => setFormData({ ...formData, quality_check_remarks: e.target.value })}
                rows={4}
                required
              />
            </div>
            
            {!formData.quality_check_passed && (
              <div className="p-3 bg-red-50 border border-red-200 rounded">
                <p className="text-sm text-red-800 font-medium">⚠️ Quality Check Failed</p>
                <p className="text-xs text-red-700 mt-1">
                  Please address quality issues before completing maintenance. You may need to re-perform the maintenance action.
                </p>
              </div>
            )}
          </div>
        )}
      </div>
      
      {/* Customer Satisfaction */}
      <div className="pt-4 border-t">
        <h3 className="text-lg font-semibold mb-4">Customer Satisfaction</h3>
        
        <div className="space-y-4">
          <div>
            <Label>Customer Rating (Optional)</Label>
            <div className="flex items-center gap-2 mt-2">
              {[1, 2, 3, 4, 5].map((rating) => (
                <button
                  key={rating}
                  type="button"
                  onClick={() => setFormData({ ...formData, customer_satisfaction_rating: rating })}
                  className={`text-3xl transition-transform hover:scale-110 ${
                    rating <= formData.customer_satisfaction_rating 
                      ? 'text-yellow-400' 
                      : 'text-gray-300'
                  }`}
                >
                  ⭐
                </button>
              ))}
              {formData.customer_satisfaction_rating > 0 && (
                <span className="ml-2 text-sm text-muted-foreground">
                  {formData.customer_satisfaction_rating}/5 stars
                </span>
              )}
            </div>
          </div>
          
          <div>
            <Label>Customer Feedback (Optional)</Label>
            <Textarea
              placeholder="Customer comments, feedback, or concerns..."
              value={formData.customer_satisfaction_feedback}
              onChange={(e) => setFormData({ ...formData, customer_satisfaction_feedback: e.target.value })}
              rows={3}
            />
          </div>
        </div>
      </div>
      
      {/* Recommendations */}
      <div className="pt-4 border-t">
        <h3 className="text-lg font-semibold mb-4">Recommendations</h3>
        <Textarea
          placeholder="Future maintenance recommendations, preventive measures, observations for next maintenance cycle..."
          value={formData.recommendations}
          onChange={(e) => setFormData({ ...formData, recommendations: e.target.value })}
          rows={4}
        />
      </div>
      
      {/* Completion Summary */}
      <div className="pt-4 border-t">
        <div className="p-4 bg-green-50 border border-green-200 rounded">
          <h4 className="font-semibold mb-2">Completion Summary</h4>
          <div className="space-y-1 text-sm">
            <p><span className="font-medium">Maintenance:</span> {maintenance.maintenance_number}</p>
            <p><span className="font-medium">Type:</span> {maintenance.maintenance_type.replace(/_/g, ' ')}</p>
            <p><span className="font-medium">Total Cost:</span> {formatCurrency(maintenance.total_maintenance_cost || 0)}</p>
            {maintenance.customer_charged && (
              <p><span className="font-medium">Customer Charged:</span> {formatCurrency(maintenance.customer_total_charge || 0)}</p>
            )}
            <p><span className="font-medium">Quality Check:</span> {
              formData.quality_check_done 
                ? (formData.quality_check_passed ? '✓ PASSED' : '✗ FAILED') 
                : 'Not performed'
            }</p>
            {formData.customer_satisfaction_rating > 0 && (
              <p><span className="font-medium">Customer Rating:</span> {'⭐'.repeat(formData.customer_satisfaction_rating)}</p>
            )}
          </div>
        </div>
      </div>
      
      {/* Action Buttons */}
      <div className="flex gap-2">
        <Button 
          type="submit" 
          disabled={completeMutation.isPending}
          className="bg-green-600 hover:bg-green-700"
        >
          {completeMutation.isPending ? 'Completing...' : 'Complete Maintenance'}
        </Button>
        <Button 
          type="button" 
          variant="outline"
          onClick={onClose}
        >
          Cancel
        </Button>
      </div>
      
      <p className="text-xs text-muted-foreground">
        * Completing maintenance will mark it as finished and cannot be undone. Ensure all details are accurate.
      </p>
    </form>
  )
}
