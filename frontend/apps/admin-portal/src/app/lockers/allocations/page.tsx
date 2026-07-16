'use client'

import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { 
  Plus, Search, Filter, Eye, Clock, AlertCircle, RefreshCw, 
  XCircle, Calendar, User, Key, FileText 
} from 'lucide-react'
import { DashboardLayout } from '@/components/layout/dashboard-layout'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Badge } from '@/components/ui/badge'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Skeleton } from '@/components/ui/skeleton'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'
import { Label } from '@/components/ui/label'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { lockerService, AllocationStatus, type LockerAllocation, LockerSize } from '@/services/locker.service'
import { formatCurrency, formatDate } from '@/lib/utils'
import { toast } from 'sonner'

export default function AllocationsPage() {
  const [page, setPage] = useState(1)
  const [search, setSearch] = useState('')
  const [statusFilter, setStatusFilter] = useState<AllocationStatus | ''>('')
  const [isCreateOpen, setIsCreateOpen] = useState(false)
  const [isRenewOpen, setIsRenewOpen] = useState(false)
  const [isCloseOpen, setIsCloseOpen] = useState(false)
  const [selectedAllocation, setSelectedAllocation] = useState<LockerAllocation | null>(null)
  const [activeTab, setActiveTab] = useState('all')

  const queryClient = useQueryClient()

  const { data, isLoading } = useQuery({
    queryKey: ['allocations', page, search, statusFilter, activeTab],
    queryFn: () => {
      const params: any = {
        skip: (page - 1) * 12,
        limit: 12,
        status: statusFilter || (activeTab === 'active' ? AllocationStatus.ACTIVE : undefined),
      }
      if (activeTab === 'expiring') {
        params.expiring_within_days = 30
      }
      return lockerService.getAllocations(params)
    },
  })

  const { data: expiringData } = useQuery({
    queryKey: ['allocations-expiring'],
    queryFn: () => lockerService.getExpiringAllocations(30),
  })

  const { data: overdueData } = useQuery({
    queryKey: ['allocations-overdue'],
    queryFn: () => lockerService.getOverdueRents(),
  })

  const createMutation = useMutation({
    mutationFn: (data: any) => lockerService.createAllocation(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['allocations'] })
      setIsCreateOpen(false)
      toast.success('Allocation created successfully')
    },
    onError: () => {
      toast.error('Failed to create allocation')
    },
  })

  const renewMutation = useMutation({
    mutationFn: ({ id, data }: { id: string; data: any }) =>
      lockerService.renewAllocation(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['allocations'] })
      setIsRenewOpen(false)
      toast.success('Allocation renewed successfully')
    },
    onError: () => {
      toast.error('Failed to renew allocation')
    },
  })

  const closeMutation = useMutation({
    mutationFn: ({ id, data }: { id: string; data: any }) =>
      lockerService.closeAllocation(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['allocations'] })
      setIsCloseOpen(false)
      toast.success('Allocation closed successfully')
    },
    onError: () => {
      toast.error('Failed to close allocation')
    },
  })

  const getStatusColor = (status: AllocationStatus) => {
    const colors = {
      active: 'bg-green-100 text-green-800',
      expired: 'bg-yellow-100 text-yellow-800',
      closed: 'bg-gray-100 text-gray-800',
      surrendered: 'bg-orange-100 text-orange-800',
      transferred: 'bg-blue-100 text-blue-800',
    }
    return colors[status] || 'bg-gray-100 text-gray-800'
  }

  const handleRenew = (allocation: LockerAllocation) => {
    setSelectedAllocation(allocation)
    setIsRenewOpen(true)
  }

  const handleClose = (allocation: LockerAllocation) => {
    setSelectedAllocation(allocation)
    setIsCloseOpen(true)
  }

  return (
    <DashboardLayout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Locker Allocations</h1>
            <p className="text-gray-600 mt-1">Manage customer locker assignments and agreements</p>
          </div>
          <Button onClick={() => setIsCreateOpen(true)}>
            <Plus className="h-4 w-4 mr-2" />
            New Allocation
          </Button>
        </div>

        {/* Alert Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <Card className="border-l-4 border-l-yellow-500">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Expiring Soon</CardTitle>
              <Clock className="h-4 w-4 text-yellow-600" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-yellow-600">
                {expiringData?.data?.expiring_allocations?.length || 0}
              </div>
              <p className="text-xs text-gray-600 mt-1">Within 30 days</p>
            </CardContent>
          </Card>
          <Card className="border-l-4 border-l-red-500">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Overdue Payments</CardTitle>
              <AlertCircle className="h-4 w-4 text-red-600" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-red-600">
                {overdueData?.data?.overdue_rents?.length || 0}
              </div>
              <p className="text-xs text-gray-600 mt-1">Requires attention</p>
            </CardContent>
          </Card>
          <Card className="border-l-4 border-l-green-500">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Active Allocations</CardTitle>
              <Key className="h-4 w-4 text-green-600" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-green-600">
                {data?.data?.allocations?.filter((a: LockerAllocation) => 
                  a.status === AllocationStatus.ACTIVE).length || 0}
              </div>
              <p className="text-xs text-gray-600 mt-1">Currently assigned</p>
            </CardContent>
          </Card>
        </div>

        {/* Tabs */}
        <Tabs value={activeTab} onValueChange={setActiveTab}>
          <TabsList>
            <TabsTrigger value="all">All Allocations</TabsTrigger>
            <TabsTrigger value="active">Active</TabsTrigger>
            <TabsTrigger value="expiring">Expiring Soon</TabsTrigger>
          </TabsList>

          <TabsContent value={activeTab} className="space-y-4">
            {/* Filters */}
            <div className="flex items-center gap-4">
              <div className="flex-1 relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
                <Input
                  type="search"
                  placeholder="Search by allocation number, customer..."
                  className="pl-10"
                  value={search}
                  onChange={(e) => setSearch(e.target.value)}
                />
              </div>
              <Select value={statusFilter} onValueChange={(value) => setStatusFilter(value as AllocationStatus | '')}>
                <SelectTrigger className="w-[180px]">
                  <SelectValue placeholder="All Status" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="">All Status</SelectItem>
                  <SelectItem value={AllocationStatus.ACTIVE}>Active</SelectItem>
                  <SelectItem value={AllocationStatus.EXPIRED}>Expired</SelectItem>
                  <SelectItem value={AllocationStatus.CLOSED}>Closed</SelectItem>
                </SelectContent>
              </Select>
              <Button variant="outline">
                <Filter className="h-4 w-4 mr-2" />
                More Filters
              </Button>
            </div>

            {/* Allocations Table */}
            <Card>
              <CardContent className="p-0">
                <div className="overflow-x-auto">
                  <table className="w-full">
                    <thead className="bg-gray-50 border-b">
                      <tr>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                          Allocation Details
                        </th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                          Customer
                        </th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                          Period
                        </th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                          Rent
                        </th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                          Status
                        </th>
                        <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">
                          Actions
                        </th>
                      </tr>
                    </thead>
                    <tbody className="bg-white divide-y divide-gray-200">
                      {isLoading ? (
                        [...Array(5)].map((_, i) => (
                          <tr key={i}>
                            <td className="px-6 py-4"><Skeleton className="h-4 w-32" /></td>
                            <td className="px-6 py-4"><Skeleton className="h-4 w-40" /></td>
                            <td className="px-6 py-4"><Skeleton className="h-4 w-32" /></td>
                            <td className="px-6 py-4"><Skeleton className="h-4 w-24" /></td>
                            <td className="px-6 py-4"><Skeleton className="h-6 w-20" /></td>
                            <td className="px-6 py-4"><Skeleton className="h-8 w-24" /></td>
                          </tr>
                        ))
                      ) : data?.data?.allocations && data.data.allocations.length > 0 ? (
                        data.data.allocations.map((allocation: LockerAllocation) => (
                          <tr key={allocation.id} className="hover:bg-gray-50">
                            <td className="px-6 py-4 whitespace-nowrap">
                              <div className="text-sm font-medium text-gray-900">
                                {allocation.allocation_number}
                              </div>
                              <div className="text-sm text-gray-500">
                                Agreement: {allocation.agreement_number}
                              </div>
                            </td>
                            <td className="px-6 py-4">
                              <div className="flex items-center">
                                <User className="h-4 w-4 text-gray-400 mr-2" />
                                <div className="text-sm text-gray-900">Customer ID: {allocation.customer_id}</div>
                              </div>
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap">
                              <div className="text-sm text-gray-900">
                                {formatDate(allocation.agreement_start_date)}
                              </div>
                              <div className="text-sm text-gray-500">
                                to {formatDate(allocation.agreement_end_date)}
                              </div>
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap">
                              <div className="text-sm font-medium text-gray-900">
                                {formatCurrency(allocation.annual_rent)}/yr
                              </div>
                              {allocation.outstanding_rent > 0 && (
                                <div className="text-xs text-red-600">
                                  Outstanding: {formatCurrency(allocation.outstanding_rent)}
                                </div>
                              )}
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap">
                              <Badge className={getStatusColor(allocation.status)}>
                                {allocation.status.toUpperCase()}
                              </Badge>
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap text-right">
                              <div className="flex items-center justify-end gap-2">
                                <Button variant="ghost" size="sm">
                                  <Eye className="h-4 w-4" />
                                </Button>
                                {allocation.status === AllocationStatus.ACTIVE && (
                                  <>
                                    <Button
                                      variant="ghost"
                                      size="sm"
                                      onClick={() => handleRenew(allocation)}
                                    >
                                      <RefreshCw className="h-4 w-4" />
                                    </Button>
                                    <Button
                                      variant="ghost"
                                      size="sm"
                                      onClick={() => handleClose(allocation)}
                                    >
                                      <XCircle className="h-4 w-4" />
                                    </Button>
                                  </>
                                )}
                              </div>
                            </td>
                          </tr>
                        ))
                      ) : (
                        <tr>
                          <td colSpan={6} className="px-6 py-12 text-center text-gray-500">
                            No allocations found
                          </td>
                        </tr>
                      )}
                    </tbody>
                  </table>
                </div>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>

        {/* Dialogs */}
        <AllocationFormDialog
          open={isCreateOpen}
          onOpenChange={setIsCreateOpen}
          onSubmit={(data) => createMutation.mutate(data)}
          isLoading={createMutation.isPending}
        />

        {selectedAllocation && (
          <>
            <RenewalDialog
              open={isRenewOpen}
              onOpenChange={setIsRenewOpen}
              allocation={selectedAllocation}
              onSubmit={(data) => renewMutation.mutate({ id: selectedAllocation.id, data })}
              isLoading={renewMutation.isPending}
            />
            <ClosureDialog
              open={isCloseOpen}
              onOpenChange={setIsCloseOpen}
              allocation={selectedAllocation}
              onSubmit={(data) => closeMutation.mutate({ id: selectedAllocation.id, data })}
              isLoading={closeMutation.isPending}
            />
          </>
        )}
      </div>
    </DashboardLayout>
  )
}

// Allocation Form Dialog Component
function AllocationFormDialog({
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
  const [formData, setFormData] = useState<any>({
    allocation_number: '',
    agreement_number: '',
    locker_id: '',
    customer_id: '',
    allocation_date: new Date().toISOString().split('T')[0],
    agreement_start_date: new Date().toISOString().split('T')[0],
    agreement_end_date: '',
    annual_rent: 0,
    security_deposit: 0,
    rent_frequency: 'annual',
    gst_applicable: true,
    gst_rate: 18,
    customer_key_number: '',
    bank_key_number: '',
    nominee_details: {
      nominee_name: '',
      nominee_relationship: '',
      nominee_dob: '',
      nominee_percentage: 100,
    },
  })

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    onSubmit(formData)
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-3xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>New Locker Allocation</DialogTitle>
          <DialogDescription>Assign a locker to a customer</DialogDescription>
        </DialogHeader>
        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Allocation Details */}
          <div className="space-y-4">
            <h3 className="text-sm font-medium">Allocation Details</h3>
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="allocation_number">Allocation Number *</Label>
                <Input
                  id="allocation_number"
                  value={formData.allocation_number}
                  onChange={(e) => setFormData({ ...formData, allocation_number: e.target.value })}
                  required
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="agreement_number">Agreement Number *</Label>
                <Input
                  id="agreement_number"
                  value={formData.agreement_number}
                  onChange={(e) => setFormData({ ...formData, agreement_number: e.target.value })}
                  required
                />
              </div>
            </div>
          </div>

          {/* Customer & Locker */}
          <div className="space-y-4">
            <h3 className="text-sm font-medium">Customer & Locker</h3>
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="customer_id">Customer ID *</Label>
                <Input
                  id="customer_id"
                  value={formData.customer_id}
                  onChange={(e) => setFormData({ ...formData, customer_id: e.target.value })}
                  required
                  placeholder="Search customer..."
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="locker_id">Locker ID *</Label>
                <Input
                  id="locker_id"
                  value={formData.locker_id}
                  onChange={(e) => setFormData({ ...formData, locker_id: e.target.value })}
                  required
                  placeholder="Select available locker..."
                />
              </div>
            </div>
          </div>

          {/* Agreement Period */}
          <div className="space-y-4">
            <h3 className="text-sm font-medium">Agreement Period</h3>
            <div className="grid grid-cols-3 gap-4">
              <div className="space-y-2">
                <Label htmlFor="allocation_date">Allocation Date</Label>
                <Input
                  id="allocation_date"
                  type="date"
                  value={formData.allocation_date}
                  onChange={(e) => setFormData({ ...formData, allocation_date: e.target.value })}
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="agreement_start_date">Start Date *</Label>
                <Input
                  id="agreement_start_date"
                  type="date"
                  value={formData.agreement_start_date}
                  onChange={(e) => setFormData({ ...formData, agreement_start_date: e.target.value })}
                  required
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="agreement_end_date">End Date *</Label>
                <Input
                  id="agreement_end_date"
                  type="date"
                  value={formData.agreement_end_date}
                  onChange={(e) => setFormData({ ...formData, agreement_end_date: e.target.value })}
                  required
                />
              </div>
            </div>
          </div>

          {/* Financial Details */}
          <div className="space-y-4">
            <h3 className="text-sm font-medium">Financial Terms</h3>
            <div className="grid grid-cols-3 gap-4">
              <div className="space-y-2">
                <Label htmlFor="annual_rent">Annual Rent (₹) *</Label>
                <Input
                  id="annual_rent"
                  type="number"
                  value={formData.annual_rent}
                  onChange={(e) => setFormData({ ...formData, annual_rent: parseFloat(e.target.value) })}
                  required
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="security_deposit">Security Deposit (₹) *</Label>
                <Input
                  id="security_deposit"
                  type="number"
                  value={formData.security_deposit}
                  onChange={(e) => setFormData({ ...formData, security_deposit: parseFloat(e.target.value) })}
                  required
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="rent_frequency">Rent Frequency</Label>
                <Select
                  value={formData.rent_frequency}
                  onValueChange={(value) => setFormData({ ...formData, rent_frequency: value })}
                >
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="monthly">Monthly</SelectItem>
                    <SelectItem value="quarterly">Quarterly</SelectItem>
                    <SelectItem value="semi_annual">Semi-Annual</SelectItem>
                    <SelectItem value="annual">Annual</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>
          </div>

          {/* Key Management */}
          <div className="space-y-4">
            <h3 className="text-sm font-medium">Key Management</h3>
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="customer_key_number">Customer Key Number</Label>
                <Input
                  id="customer_key_number"
                  value={formData.customer_key_number}
                  onChange={(e) => setFormData({ ...formData, customer_key_number: e.target.value })}
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="bank_key_number">Bank Key Number</Label>
                <Input
                  id="bank_key_number"
                  value={formData.bank_key_number}
                  onChange={(e) => setFormData({ ...formData, bank_key_number: e.target.value })}
                />
              </div>
            </div>
          </div>

          {/* Nominee Details */}
          <div className="space-y-4">
            <h3 className="text-sm font-medium">Nominee Details (Optional)</h3>
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="nominee_name">Nominee Name</Label>
                <Input
                  id="nominee_name"
                  value={formData.nominee_details.nominee_name}
                  onChange={(e) => setFormData({
                    ...formData,
                    nominee_details: { ...formData.nominee_details, nominee_name: e.target.value }
                  })}
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="nominee_relationship">Relationship</Label>
                <Input
                  id="nominee_relationship"
                  value={formData.nominee_details.nominee_relationship}
                  onChange={(e) => setFormData({
                    ...formData,
                    nominee_details: { ...formData.nominee_details, nominee_relationship: e.target.value }
                  })}
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="nominee_dob">Date of Birth</Label>
                <Input
                  id="nominee_dob"
                  type="date"
                  value={formData.nominee_details.nominee_dob}
                  onChange={(e) => setFormData({
                    ...formData,
                    nominee_details: { ...formData.nominee_details, nominee_dob: e.target.value }
                  })}
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="nominee_percentage">Percentage (%)</Label>
                <Input
                  id="nominee_percentage"
                  type="number"
                  min="0"
                  max="100"
                  value={formData.nominee_details.nominee_percentage}
                  onChange={(e) => setFormData({
                    ...formData,
                    nominee_details: { ...formData.nominee_details, nominee_percentage: parseFloat(e.target.value) }
                  })}
                />
              </div>
            </div>
          </div>

          <DialogFooter>
            <Button type="button" variant="outline" onClick={() => onOpenChange(false)}>
              Cancel
            </Button>
            <Button type="submit" disabled={isLoading}>
              {isLoading ? 'Creating...' : 'Create Allocation'}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  )
}

// Renewal Dialog Component
function RenewalDialog({
  open,
  onOpenChange,
  allocation,
  onSubmit,
  isLoading,
}: {
  open: boolean
  onOpenChange: (open: boolean) => void
  allocation: LockerAllocation
  onSubmit: (data: any) => void
  isLoading: boolean
}) {
  const [formData, setFormData] = useState({
    new_end_date: '',
    annual_rent: allocation.annual_rent,
    adjust_security_deposit: false,
    additional_deposit: 0,
    remarks: '',
  })

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    onSubmit(formData)
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Renew Allocation</DialogTitle>
          <DialogDescription>
            Renewing allocation: {allocation.allocation_number}
          </DialogDescription>
        </DialogHeader>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="new_end_date">New End Date *</Label>
            <Input
              id="new_end_date"
              type="date"
              value={formData.new_end_date}
              onChange={(e) => setFormData({ ...formData, new_end_date: e.target.value })}
              required
            />
          </div>
          <div className="space-y-2">
            <Label htmlFor="annual_rent">Annual Rent (₹) *</Label>
            <Input
              id="annual_rent"
              type="number"
              value={formData.annual_rent}
              onChange={(e) => setFormData({ ...formData, annual_rent: parseFloat(e.target.value) })}
              required
            />
          </div>
          <div className="space-y-2">
            <Label htmlFor="additional_deposit">Additional Deposit (₹)</Label>
            <Input
              id="additional_deposit"
              type="number"
              value={formData.additional_deposit}
              onChange={(e) => setFormData({ ...formData, additional_deposit: parseFloat(e.target.value) })}
            />
          </div>
          <div className="space-y-2">
            <Label htmlFor="remarks">Remarks</Label>
            <Input
              id="remarks"
              value={formData.remarks}
              onChange={(e) => setFormData({ ...formData, remarks: e.target.value })}
            />
          </div>
          <DialogFooter>
            <Button type="button" variant="outline" onClick={() => onOpenChange(false)}>
              Cancel
            </Button>
            <Button type="submit" disabled={isLoading}>
              {isLoading ? 'Renewing...' : 'Renew'}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  )
}

// Closure Dialog Component
function ClosureDialog({
  open,
  onOpenChange,
  allocation,
  onSubmit,
  isLoading,
}: {
  open: boolean
  onOpenChange: (open: boolean) => void
  allocation: LockerAllocation
  onSubmit: (data: any) => void
  isLoading: boolean
}) {
  const [formData, setFormData] = useState({
    closure_date: new Date().toISOString().split('T')[0],
    closure_reason: '',
    refund_security_deposit: true,
    closure_charges: 0,
    remarks: '',
  })

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    onSubmit(formData)
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Close Allocation</DialogTitle>
          <DialogDescription>
            Closing allocation: {allocation.allocation_number}
          </DialogDescription>
        </DialogHeader>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="closure_date">Closure Date *</Label>
            <Input
              id="closure_date"
              type="date"
              value={formData.closure_date}
              onChange={(e) => setFormData({ ...formData, closure_date: e.target.value })}
              required
            />
          </div>
          <div className="space-y-2">
            <Label htmlFor="closure_reason">Reason *</Label>
            <Select
              value={formData.closure_reason}
              onValueChange={(value) => setFormData({ ...formData, closure_reason: value })}
            >
              <SelectTrigger>
                <SelectValue placeholder="Select reason" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="customer_request">Customer Request</SelectItem>
                <SelectItem value="non_payment">Non-Payment</SelectItem>
                <SelectItem value="relocated">Customer Relocated</SelectItem>
                <SelectItem value="other">Other</SelectItem>
              </SelectContent>
            </Select>
          </div>
          <div className="space-y-2">
            <Label htmlFor="closure_charges">Closure Charges (₹)</Label>
            <Input
              id="closure_charges"
              type="number"
              value={formData.closure_charges}
              onChange={(e) => setFormData({ ...formData, closure_charges: parseFloat(e.target.value) })}
            />
          </div>
          <div className="flex items-center space-x-2">
            <input
              type="checkbox"
              id="refund_security_deposit"
              checked={formData.refund_security_deposit}
              onChange={(e) => setFormData({ ...formData, refund_security_deposit: e.target.checked })}
              className="rounded"
            />
            <Label htmlFor="refund_security_deposit">Refund Security Deposit</Label>
          </div>
          <div className="space-y-2">
            <Label htmlFor="remarks">Remarks</Label>
            <Input
              id="remarks"
              value={formData.remarks}
              onChange={(e) => setFormData({ ...formData, remarks: e.target.value })}
            />
          </div>
          <DialogFooter>
            <Button type="button" variant="outline" onClick={() => onOpenChange(false)}>
              Cancel
            </Button>
            <Button type="submit" disabled={isLoading} className="bg-red-600 hover:bg-red-700">
              {isLoading ? 'Closing...' : 'Close Allocation'}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  )
}
