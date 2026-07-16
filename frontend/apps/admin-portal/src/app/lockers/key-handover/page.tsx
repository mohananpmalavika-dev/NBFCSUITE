'use client'

import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@antml:react-query'
import { 
  Key, Plus, Search, Filter, Eye, AlertTriangle, CheckCircle, 
  XCircle, Clock, Shield, FileText, UserCheck, Fingerprint
} from 'lucide-react'
import { DashboardLayout } from '@/components/layout/dashboard-layout'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Badge } from '@/components/ui/badge'
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card'
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
import { Textarea } from '@/components/ui/textarea'
import { Checkbox } from '@/components/ui/checkbox'
import { 
  keyHandoverService, 
  KeyStatus,
  HandoverType,
  KeyType,
  type LockerKeyHandover 
} from '@/services/locker.service'
import { formatCurrency, formatDate } from '@/lib/utils'
import { toast } from 'sonner'

export default function KeyHandoverPage() {
  const [page, setPage] = useState(1)
  const [search, setSearch] = useState('')
  const [statusFilter, setStatusFilter] = useState<KeyStatus | ''>('')
  const [typeFilter, setTypeFilter] = useState<HandoverType | ''>('')
  const [isIssueOpen, setIsIssueOpen] = useState(false)
  const [isReturnOpen, setIsReturnOpen] = useState(false)
  const [isLostKeyOpen, setIsLostKeyOpen] = useState(false)
  const [isViewOpen, setIsViewOpen] = useState(false)
  const [selectedHandover, setSelectedHandover] = useState<LockerKeyHandover | null>(null)
  const [activeTab, setActiveTab] = useState('all')

  const queryClient = useQueryClient()

  const { data, isLoading } = useQuery({
    queryKey: ['key-handovers', page, search, statusFilter, typeFilter, activeTab],
    queryFn: () => {
      const params: any = {
        skip: (page - 1) * 12,
        limit: 12,
      }
      if (statusFilter) params.status = statusFilter
      if (typeFilter) params.handover_type = typeFilter
      if (activeTab === 'active') params.status = KeyStatus.ACTIVE
      if (activeTab === 'lost') params.status = KeyStatus.LOST
      return keyHandoverService.listKeyHandovers(params)
    },
  })

  const { data: statisticsData } = useQuery({
    queryKey: ['key-handover-statistics'],
    queryFn: () => keyHandoverService.getStatistics(),
  })

  const { data: lostKeysData } = useQuery({
    queryKey: ['lost-keys-pending'],
    queryFn: () => keyHandoverService.getLostKeysPendingAction(),
  })

  const issueKeysMutation = useMutation({
    mutationFn: (data: any) => keyHandoverService.issueKeys(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['key-handovers'] })
      queryClient.invalidateQueries({ queryKey: ['key-handover-statistics'] })
      setIsIssueOpen(false)
      toast.success('Keys issued successfully')
    },
    onError: () => {
      toast.error('Failed to issue keys')
    },
  })

  const returnKeysMutation = useMutation({
    mutationFn: (data: any) => keyHandoverService.returnKeys(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['key-handovers'] })
      queryClient.invalidateQueries({ queryKey: ['key-handover-statistics'] })
      setIsReturnOpen(false)
      toast.success('Keys returned successfully')
    },
    onError: () => {
      toast.error('Failed to process key return')
    },
  })

  const reportLostKeyMutation = useMutation({
    mutationFn: (data: any) => keyHandoverService.reportLostKey(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['key-handovers'] })
      queryClient.invalidateQueries({ queryKey: ['lost-keys-pending'] })
      setIsLostKeyOpen(false)
      toast.success('Lost key reported successfully')
    },
    onError: () => {
      toast.error('Failed to report lost key')
    },
  })

  const getStatusColor = (status: KeyStatus) => {
    const colors = {
      active: 'bg-green-100 text-green-800',
      returned: 'bg-blue-100 text-blue-800',
      lost: 'bg-red-100 text-red-800',
      duplicate_issued: 'bg-yellow-100 text-yellow-800',
      broken: 'bg-orange-100 text-orange-800',
    }
    return colors[status] || 'bg-gray-100 text-gray-800'
  }

  const getTypeIcon = (type: HandoverType) => {
    const icons = {
      issuance: Key,
      return: CheckCircle,
      lost_report: AlertTriangle,
      duplicate_issue: Key,
      breaking: XCircle,
    }
    return icons[type] || Key
  }

  const handleView = (handover: LockerKeyHandover) => {
    setSelectedHandover(handover)
    setIsViewOpen(true)
  }

  const handleReturn = (handover: LockerKeyHandover) => {
    setSelectedHandover(handover)
    setIsReturnOpen(true)
  }

  const handleReportLost = (handover: LockerKeyHandover) => {
    setSelectedHandover(handover)
    setIsLostKeyOpen(true)
  }

  return (
    <DashboardLayout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Key Handover Management</h1>
            <p className="text-gray-600 mt-1">Manage dual key system and key lifecycle</p>
          </div>
          <Button onClick={() => setIsIssueOpen(true)}>
            <Plus className="h-4 w-4 mr-2" />
            Issue Keys
          </Button>
        </div>

        {/* Statistics Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <Card className="border-l-4 border-l-green-500">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Active Keys</CardTitle>
              <Key className="h-4 w-4 text-green-600" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-green-600">
                {statisticsData?.data?.active_keys || 0}
              </div>
              <p className="text-xs text-gray-600 mt-1">Currently issued</p>
            </CardContent>
          </Card>

          <Card className="border-l-4 border-l-red-500">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Lost Keys</CardTitle>
              <AlertTriangle className="h-4 w-4 text-red-600" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-red-600">
                {lostKeysData?.data?.lost_keys?.length || 0}
              </div>
              <p className="text-xs text-gray-600 mt-1">Pending action</p>
            </CardContent>
          </Card>

          <Card className="border-l-4 border-l-yellow-500">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Duplicate Keys</CardTitle>
              <Key className="h-4 w-4 text-yellow-600" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-yellow-600">
                {statisticsData?.data?.duplicate_keys_issued || 0}
              </div>
              <p className="text-xs text-gray-600 mt-1">Issued</p>
            </CardContent>
          </Card>

          <Card className="border-l-4 border-l-blue-500">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Total Handovers</CardTitle>
              <FileText className="h-4 w-4 text-blue-600" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-blue-600">
                {statisticsData?.data?.total_handovers || 0}
              </div>
              <p className="text-xs text-gray-600 mt-1">All time</p>
            </CardContent>
          </Card>
        </div>

        {/* Dual Key System Info */}
        <Card className="bg-gradient-to-r from-blue-50 to-purple-50">
          <CardContent className="pt-6">
            <div className="flex items-start gap-4">
              <div className="p-3 bg-blue-100 rounded-lg">
                <Shield className="h-6 w-6 text-blue-600" />
              </div>
              <div className="flex-1">
                <h3 className="font-medium text-gray-900 mb-2">Dual Key System</h3>
                <p className="text-sm text-gray-600 mb-3">
                  Each locker requires both customer key and bank master key for access. This ensures maximum security.
                </p>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-sm">
                  <div className="flex items-center gap-2">
                    <div className="w-2 h-2 rounded-full bg-green-500"></div>
                    <span>Customer Key: Issued to customer</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <div className="w-2 h-2 rounded-full bg-purple-500"></div>
                    <span>Bank Master Key: Kept at branch</span>
                  </div>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Tabs */}
        <Tabs value={activeTab} onValueChange={setActiveTab}>
          <TabsList>
            <TabsTrigger value="all">All Handovers</TabsTrigger>
            <TabsTrigger value="active">Active Keys</TabsTrigger>
            <TabsTrigger value="lost">Lost Keys</TabsTrigger>
          </TabsList>

          <TabsContent value={activeTab} className="space-y-4">
            {/* Filters */}
            <div className="flex items-center gap-4">
              <div className="flex-1 relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
                <Input
                  type="search"
                  placeholder="Search by allocation, customer, key number..."
                  className="pl-10"
                  value={search}
                  onChange={(e) => setSearch(e.target.value)}
                />
              </div>
              <Select value={statusFilter} onValueChange={(value) => setStatusFilter(value as KeyStatus | '')}>
                <SelectTrigger className="w-[180px]">
                  <SelectValue placeholder="All Status" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="">All Status</SelectItem>
                  <SelectItem value={KeyStatus.ACTIVE}>Active</SelectItem>
                  <SelectItem value={KeyStatus.RETURNED}>Returned</SelectItem>
                  <SelectItem value={KeyStatus.LOST}>Lost</SelectItem>
                  <SelectItem value={KeyStatus.DUPLICATE_ISSUED}>Duplicate Issued</SelectItem>
                </SelectContent>
              </Select>
              <Select value={typeFilter} onValueChange={(value) => setTypeFilter(value as HandoverType | '')}>
                <SelectTrigger className="w-[180px]">
                  <SelectValue placeholder="All Types" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="">All Types</SelectItem>
                  <SelectItem value={HandoverType.ISSUANCE}>Issuance</SelectItem>
                  <SelectItem value={HandoverType.RETURN}>Return</SelectItem>
                  <SelectItem value={HandoverType.LOST_REPORT}>Lost Report</SelectItem>
                  <SelectItem value={HandoverType.DUPLICATE_ISSUE}>Duplicate Issue</SelectItem>
                </SelectContent>
              </Select>
            </div>

            {/* Handovers Table */}
            <Card>
              <CardContent className="p-0">
                <div className="overflow-x-auto">
                  <table className="w-full">
                    <thead className="bg-gray-50 border-b">
                      <tr>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                          Handover Details
                        </th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                          Keys
                        </th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                          Customer
                        </th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                          Date
                        </th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                          Biometric
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
                            <td className="px-6 py-4"><Skeleton className="h-4 w-20" /></td>
                            <td className="px-6 py-4"><Skeleton className="h-6 w-24" /></td>
                            <td className="px-6 py-4"><Skeleton className="h-8 w-24" /></td>
                          </tr>
                        ))
                      ) : data?.data?.handovers && data.data.handovers.length > 0 ? (
                        data.data.handovers.map((handover: LockerKeyHandover) => (
                          <tr key={handover.id} className="hover:bg-gray-50">
                            <td className="px-6 py-4 whitespace-nowrap">
                              <div className="flex items-center gap-2">
                                {(() => {
                                  const Icon = getTypeIcon(handover.handover_type)
                                  return <Icon className="h-4 w-4 text-gray-400" />
                                })()}
                                <div>
                                  <div className="text-sm font-medium text-gray-900">
                                    {handover.handover_type.replace('_', ' ').toUpperCase()}
                                  </div>
                                  <div className="text-xs text-gray-500">
                                    Alloc: {handover.allocation_id}
                                  </div>
                                </div>
                              </div>
                            </td>
                            <td className="px-6 py-4">
                              <div className="space-y-1">
                                <div className="text-sm text-gray-900 flex items-center gap-2">
                                  <Key className="h-3 w-3 text-green-600" />
                                  <span>Customer: {handover.customer_key_number}</span>
                                </div>
                                <div className="text-sm text-gray-900 flex items-center gap-2">
                                  <Shield className="h-3 w-3 text-purple-600" />
                                  <span>Bank: {handover.bank_key_number}</span>
                                </div>
                              </div>
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap">
                              <div className="text-sm text-gray-900">
                                ID: {handover.customer_id}
                              </div>
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap">
                              <div className="text-sm text-gray-900">
                                {formatDate(handover.handover_date)}
                              </div>
                              {handover.return_date && (
                                <div className="text-xs text-gray-500">
                                  Returned: {formatDate(handover.return_date)}
                                </div>
                              )}
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap">
                              {handover.biometric_captured ? (
                                <div className="flex items-center gap-1 text-green-600">
                                  <Fingerprint className="h-4 w-4" />
                                  <span className="text-xs">Captured</span>
                                </div>
                              ) : (
                                <div className="flex items-center gap-1 text-gray-400">
                                  <Fingerprint className="h-4 w-4" />
                                  <span className="text-xs">No</span>
                                </div>
                              )}
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap">
                              <Badge className={getStatusColor(handover.key_status)}>
                                {handover.key_status.replace('_', ' ').toUpperCase()}
                              </Badge>
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap text-right">
                              <div className="flex items-center justify-end gap-2">
                                <Button
                                  variant="ghost"
                                  size="sm"
                                  onClick={() => handleView(handover)}
                                >
                                  <Eye className="h-4 w-4" />
                                </Button>
                                {handover.key_status === KeyStatus.ACTIVE && (
                                  <>
                                    <Button
                                      variant="ghost"
                                      size="sm"
                                      className="text-blue-600"
                                      onClick={() => handleReturn(handover)}
                                    >
                                      <CheckCircle className="h-4 w-4" />
                                    </Button>
                                    <Button
                                      variant="ghost"
                                      size="sm"
                                      className="text-red-600"
                                      onClick={() => handleReportLost(handover)}
                                    >
                                      <AlertTriangle className="h-4 w-4" />
                                    </Button>
                                  </>
                                )}
                              </div>
                            </td>
                          </tr>
                        ))
                      ) : (
                        <tr>
                          <td colSpan={7} className="px-6 py-12 text-center text-gray-500">
                            No key handovers found
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
        <IssueKeysDialog
          open={isIssueOpen}
          onOpenChange={setIsIssueOpen}
          onSubmit={(data) => issueKeysMutation.mutate(data)}
          isLoading={issueKeysMutation.isPending}
        />

        {selectedHandover && (
          <>
            <ReturnKeysDialog
              open={isReturnOpen}
              onOpenChange={setIsReturnOpen}
              handover={selectedHandover}
              onSubmit={(data) => returnKeysMutation.mutate(data)}
              isLoading={returnKeysMutation.isPending}
            />
            <ReportLostKeyDialog
              open={isLostKeyOpen}
              onOpenChange={setIsLostKeyOpen}
              handover={selectedHandover}
              onSubmit={(data) => reportLostKeyMutation.mutate(data)}
              isLoading={reportLostKeyMutation.isPending}
            />
            <ViewHandoverDialog
              open={isViewOpen}
              onOpenChange={setIsViewOpen}
              handover={selectedHandover}
            />
          </>
        )}
      </div>
    </DashboardLayout>
  )
}

// Issue Keys Dialog Component
function IssueKeysDialog({
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
    allocation_id: '',
    customer_id: '',
    handover_date: new Date().toISOString().split('T')[0],
    customer_key_number: '',
    bank_key_number: '',
    witness_name: '',
    witness_id: '',
    biometric_captured: false,
    key_tested: false,
    lock_tested: false,
    remarks: '',
  })

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    onSubmit(formData)
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-3xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>Issue Locker Keys</DialogTitle>
          <DialogDescription>Issue dual keys to customer</DialogDescription>
        </DialogHeader>

        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Basic Information */}
          <div className="space-y-4">
            <h3 className="text-sm font-medium">Basic Information</h3>
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="allocation_id">Allocation ID *</Label>
                <Input
                  id="allocation_id"
                  value={formData.allocation_id}
                  onChange={(e) => setFormData({ ...formData, allocation_id: e.target.value })}
                  required
                  placeholder="Search allocation..."
                />
              </div>
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
                <Label htmlFor="handover_date">Handover Date</Label>
                <Input
                  id="handover_date"
                  type="date"
                  value={formData.handover_date}
                  onChange={(e) => setFormData({ ...formData, handover_date: e.target.value })}
                />
              </div>
            </div>
          </div>

          {/* Key Information */}
          <div className="space-y-4 border-t pt-4">
            <h3 className="text-sm font-medium">Key Information</h3>
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="customer_key_number" className="flex items-center gap-2">
                  <Key className="h-4 w-4 text-green-600" />
                  Customer Key Number *
                </Label>
                <Input
                  id="customer_key_number"
                  value={formData.customer_key_number}
                  onChange={(e) => setFormData({ ...formData, customer_key_number: e.target.value })}
                  required
                  placeholder="CK-XXXX"
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="bank_key_number" className="flex items-center gap-2">
                  <Shield className="h-4 w-4 text-purple-600" />
                  Bank Master Key Number *
                </Label>
                <Input
                  id="bank_key_number"
                  value={formData.bank_key_number}
                  onChange={(e) => setFormData({ ...formData, bank_key_number: e.target.value })}
                  required
                  placeholder="BK-XXXX"
                />
              </div>
            </div>
          </div>

          {/* Witness Information */}
          <div className="space-y-4 border-t pt-4">
            <h3 className="text-sm font-medium">Witness Information</h3>
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="witness_name">Witness Name *</Label>
                <Input
                  id="witness_name"
                  value={formData.witness_name}
                  onChange={(e) => setFormData({ ...formData, witness_name: e.target.value })}
                  required
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="witness_id">Witness ID *</Label>
                <Input
                  id="witness_id"
                  value={formData.witness_id}
                  onChange={(e) => setFormData({ ...formData, witness_id: e.target.value })}
                  required
                />
              </div>
            </div>
          </div>

          {/* Verification Checklist */}
          <div className="space-y-4 border-t pt-4">
            <h3 className="text-sm font-medium">Verification Checklist</h3>
            <div className="space-y-3">
              <div className="flex items-center space-x-2">
                <Checkbox
                  id="biometric_captured"
                  checked={formData.biometric_captured}
                  onCheckedChange={(checked) => 
                    setFormData({ ...formData, biometric_captured: checked })
                  }
                />
                <Label htmlFor="biometric_captured" className="flex items-center gap-2 cursor-pointer">
                  <Fingerprint className="h-4 w-4 text-blue-600" />
                  Biometric Captured
                </Label>
              </div>
              <div className="flex items-center space-x-2">
                <Checkbox
                  id="key_tested"
                  checked={formData.key_tested}
                  onCheckedChange={(checked) => 
                    setFormData({ ...formData, key_tested: checked })
                  }
                />
                <Label htmlFor="key_tested" className="cursor-pointer">
                  Customer Key Tested
                </Label>
              </div>
              <div className="flex items-center space-x-2">
                <Checkbox
                  id="lock_tested"
                  checked={formData.lock_tested}
                  onCheckedChange={(checked) => 
                    setFormData({ ...formData, lock_tested: checked })
                  }
                />
                <Label htmlFor="lock_tested" className="cursor-pointer">
                  Lock Mechanism Tested
                </Label>
              </div>
            </div>
          </div>

          {/* Remarks */}
          <div className="space-y-2">
            <Label htmlFor="remarks">Remarks</Label>
            <Textarea
              id="remarks"
              value={formData.remarks}
              onChange={(e) => setFormData({ ...formData, remarks: e.target.value })}
              placeholder="Any additional notes..."
              rows={3}
            />
          </div>

          <DialogFooter>
            <Button type="button" variant="outline" onClick={() => onOpenChange(false)}>
              Cancel
            </Button>
            <Button type="submit" disabled={isLoading}>
              {isLoading ? 'Issuing...' : 'Issue Keys'}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  )
}

// Return Keys Dialog Component
function ReturnKeysDialog({
  open,
  onOpenChange,
  handover,
  onSubmit,
  isLoading,
}: {
  open: boolean
  onOpenChange: (open: boolean) => void
  handover: LockerKeyHandover
  onSubmit: (data: any) => void
  isLoading: boolean
}) {
  const [formData, setFormData] = useState({
    handover_id: handover.id,
    return_date: new Date().toISOString().split('T')[0],
    keys_returned_condition: 'good',
    deposit_refunded: true,
    refund_amount: 0,
    remarks: '',
  })

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    onSubmit(formData)
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-2xl">
        <DialogHeader>
          <DialogTitle>Return Keys</DialogTitle>
          <DialogDescription>
            Process key return for allocation {handover.allocation_id}
          </DialogDescription>
        </DialogHeader>

        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Handover Summary */}
          <Card className="bg-blue-50 border-blue-200">
            <CardContent className="pt-6">
              <div className="grid grid-cols-2 gap-4 text-sm">
                <div>
                  <p className="text-gray-600">Allocation ID</p>
                  <p className="font-medium">{handover.allocation_id}</p>
                </div>
                <div>
                  <p className="text-gray-600">Customer ID</p>
                  <p className="font-medium">{handover.customer_id}</p>
                </div>
                <div>
                  <p className="text-gray-600">Customer Key</p>
                  <p className="font-medium">{handover.customer_key_number}</p>
                </div>
                <div>
                  <p className="text-gray-600">Bank Key</p>
                  <p className="font-medium">{handover.bank_key_number}</p>
                </div>
                <div>
                  <p className="text-gray-600">Issued Date</p>
                  <p className="font-medium">{formatDate(handover.handover_date)}</p>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Return Details */}
          <div className="space-y-4">
            <h3 className="text-sm font-medium">Return Details</h3>
            
            <div className="space-y-2">
              <Label htmlFor="return_date">Return Date</Label>
              <Input
                id="return_date"
                type="date"
                value={formData.return_date}
                onChange={(e) => setFormData({ ...formData, return_date: e.target.value })}
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="keys_returned_condition">Keys Condition</Label>
              <Select
                value={formData.keys_returned_condition}
                onValueChange={(value) => setFormData({ ...formData, keys_returned_condition: value })}
              >
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="good">Good</SelectItem>
                  <SelectItem value="fair">Fair</SelectItem>
                  <SelectItem value="damaged">Damaged</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-2">
              <Label htmlFor="refund_amount">Deposit Refund Amount (₹)</Label>
              <Input
                id="refund_amount"
                type="number"
                min="0"
                value={formData.refund_amount}
                onChange={(e) => setFormData({ ...formData, refund_amount: parseFloat(e.target.value) })}
              />
            </div>

            <div className="flex items-center space-x-2">
              <Checkbox
                id="deposit_refunded"
                checked={formData.deposit_refunded}
                onCheckedChange={(checked) => 
                  setFormData({ ...formData, deposit_refunded: checked as boolean })
                }
              />
              <Label htmlFor="deposit_refunded" className="cursor-pointer">
                Security Deposit Refunded
              </Label>
            </div>

            <div className="space-y-2">
              <Label htmlFor="remarks">Remarks</Label>
              <Textarea
                id="remarks"
                value={formData.remarks}
                onChange={(e) => setFormData({ ...formData, remarks: e.target.value })}
                placeholder="Any observations during key return..."
                rows={3}
              />
            </div>
          </div>

          <div className="bg-green-50 border border-green-200 rounded-lg p-4">
            <div className="flex items-start gap-3">
              <CheckCircle className="h-5 w-5 text-green-600 mt-0.5" />
              <div className="text-sm text-green-900">
                <p className="font-medium mb-1">Return Checklist</p>
                <ul className="list-disc list-inside space-y-1 text-green-800">
                  <li>Verify both customer and bank keys are returned</li>
                  <li>Check key condition and report any damage</li>
                  <li>Process security deposit refund if applicable</li>
                  <li>Update locker status to available</li>
                </ul>
              </div>
            </div>
          </div>

          <DialogFooter>
            <Button type="button" variant="outline" onClick={() => onOpenChange(false)}>
              Cancel
            </Button>
            <Button type="submit" disabled={isLoading} className="bg-blue-600 hover:bg-blue-700">
              {isLoading ? 'Processing...' : 'Process Return'}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  )
}

// Report Lost Key Dialog Component
function ReportLostKeyDialog({
  open,
  onOpenChange,
  handover,
  onSubmit,
  isLoading,
}: {
  open: boolean
  onOpenChange: (open: boolean) => void
  handover: LockerKeyHandover
  onSubmit: (data: any) => void
  isLoading: boolean
}) {
  const [formData, setFormData] = useState({
    handover_id: handover.id,
    lost_date: new Date().toISOString().split('T')[0],
    lost_key_type: KeyType.CUSTOMER_KEY,
    reported_by: '',
    fir_number: '',
    fir_date: '',
    indemnity_bond_received: false,
    duplicate_key_required: true,
    duplicate_key_charges: 0,
    remarks: '',
  })

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    onSubmit(formData)
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-3xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>Report Lost Key</DialogTitle>
          <DialogDescription>
            Report and document lost key for allocation {handover.allocation_id}
          </DialogDescription>
        </DialogHeader>

        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Handover Summary */}
          <Card className="bg-red-50 border-red-200">
            <CardContent className="pt-6">
              <div className="grid grid-cols-2 gap-4 text-sm">
                <div>
                  <p className="text-gray-600">Allocation ID</p>
                  <p className="font-medium">{handover.allocation_id}</p>
                </div>
                <div>
                  <p className="text-gray-600">Customer ID</p>
                  <p className="font-medium">{handover.customer_id}</p>
                </div>
                <div>
                  <p className="text-gray-600">Customer Key</p>
                  <p className="font-medium">{handover.customer_key_number}</p>
                </div>
                <div>
                  <p className="text-gray-600">Bank Key</p>
                  <p className="font-medium">{handover.bank_key_number}</p>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Lost Key Details */}
          <div className="space-y-4">
            <h3 className="text-sm font-medium">Lost Key Details</h3>
            
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="lost_date">Date Key Lost *</Label>
                <Input
                  id="lost_date"
                  type="date"
                  value={formData.lost_date}
                  onChange={(e) => setFormData({ ...formData, lost_date: e.target.value })}
                  required
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="lost_key_type">Lost Key Type *</Label>
                <Select
                  value={formData.lost_key_type}
                  onValueChange={(value) => setFormData({ ...formData, lost_key_type: value as KeyType })}
                >
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value={KeyType.CUSTOMER_KEY}>Customer Key</SelectItem>
                    <SelectItem value={KeyType.BANK_MASTER_KEY}>Bank Master Key</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>

            <div className="space-y-2">
              <Label htmlFor="reported_by">Reported By *</Label>
              <Input
                id="reported_by"
                value={formData.reported_by}
                onChange={(e) => setFormData({ ...formData, reported_by: e.target.value })}
                required
                placeholder="Customer name or staff ID"
              />
            </div>
          </div>

          {/* Police Report */}
          <div className="space-y-4 border-t pt-4">
            <h3 className="text-sm font-medium">Police Report (FIR)</h3>
            
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="fir_number">FIR Number</Label>
                <Input
                  id="fir_number"
                  value={formData.fir_number}
                  onChange={(e) => setFormData({ ...formData, fir_number: e.target.value })}
                  placeholder="e.g., FIR/2024/XXXX"
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="fir_date">FIR Date</Label>
                <Input
                  id="fir_date"
                  type="date"
                  value={formData.fir_date}
                  onChange={(e) => setFormData({ ...formData, fir_date: e.target.value })}
                />
              </div>
            </div>

            <div className="flex items-center space-x-2">
              <Checkbox
                id="indemnity_bond_received"
                checked={formData.indemnity_bond_received}
                onCheckedChange={(checked) => 
                  setFormData({ ...formData, indemnity_bond_received: checked as boolean })
                }
              />
              <Label htmlFor="indemnity_bond_received" className="cursor-pointer">
                Indemnity Bond Received
              </Label>
            </div>
          </div>

          {/* Duplicate Key */}
          <div className="space-y-4 border-t pt-4">
            <h3 className="text-sm font-medium">Duplicate Key</h3>
            
            <div className="flex items-center space-x-2">
              <Checkbox
                id="duplicate_key_required"
                checked={formData.duplicate_key_required}
                onCheckedChange={(checked) => 
                  setFormData({ ...formData, duplicate_key_required: checked as boolean })
                }
              />
              <Label htmlFor="duplicate_key_required" className="cursor-pointer">
                Duplicate Key Required
              </Label>
            </div>

            {formData.duplicate_key_required && (
              <div className="space-y-2">
                <Label htmlFor="duplicate_key_charges">Duplicate Key Charges (₹) *</Label>
                <Input
                  id="duplicate_key_charges"
                  type="number"
                  min="0"
                  value={formData.duplicate_key_charges}
                  onChange={(e) => setFormData({ ...formData, duplicate_key_charges: parseFloat(e.target.value) })}
                />
                <p className="text-xs text-gray-500">Standard charges will be applied if left at 0</p>
              </div>
            )}
          </div>

          {/* Remarks */}
          <div className="space-y-2">
            <Label htmlFor="remarks">Detailed Remarks *</Label>
            <Textarea
              id="remarks"
              value={formData.remarks}
              onChange={(e) => setFormData({ ...formData, remarks: e.target.value })}
              placeholder="Describe circumstances of key loss..."
              rows={4}
              required
            />
          </div>

          {/* Warning */}
          <div className="bg-red-50 border border-red-200 rounded-lg p-4">
            <div className="flex items-start gap-3">
              <AlertTriangle className="h-5 w-5 text-red-600 mt-0.5" />
              <div className="text-sm text-red-900">
                <p className="font-medium mb-1">Lost Key Procedure</p>
                <ul className="list-disc list-inside space-y-1 text-red-800">
                  <li>Police FIR must be filed for lost keys</li>
                  <li>Indemnity bond required from customer</li>
                  <li>Duplicate key charges will be levied</li>
                  <li>Security measures will be enhanced</li>
                  <li>Consider locker breaking if necessary</li>
                </ul>
              </div>
            </div>
          </div>

          <DialogFooter>
            <Button type="button" variant="outline" onClick={() => onOpenChange(false)}>
              Cancel
            </Button>
            <Button type="submit" disabled={isLoading} className="bg-red-600 hover:bg-red-700">
              {isLoading ? 'Reporting...' : 'Report Lost Key'}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  )
}

// View Handover Dialog Component
function ViewHandoverDialog({
  open,
  onOpenChange,
  handover,
}: {
  open: boolean
  onOpenChange: (open: boolean) => void
  handover: LockerKeyHandover
}) {
  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-3xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>Key Handover Details</DialogTitle>
          <DialogDescription>
            Handover Type: {handover.handover_type.replace('_', ' ').toUpperCase()}
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-6">
          {/* Status Banner */}
          <div className={`p-4 rounded-lg border-l-4 ${
            handover.key_status === KeyStatus.ACTIVE ? 'bg-green-50 border-green-500' :
            handover.key_status === KeyStatus.RETURNED ? 'bg-blue-50 border-blue-500' :
            handover.key_status === KeyStatus.LOST ? 'bg-red-50 border-red-500' :
            'bg-gray-50 border-gray-500'
          }`}>
            <div className="flex items-center justify-between">
              <div>
                <p className="font-medium">Status: {handover.key_status.replace('_', ' ').toUpperCase()}</p>
                <p className="text-sm mt-1">Type: {handover.handover_type.replace('_', ' ')}</p>
              </div>
              <Badge className={getStatusColor(handover.key_status)}>
                {handover.key_status.replace('_', ' ').toUpperCase()}
              </Badge>
            </div>
          </div>

          {/* Basic Information */}
          <div className="space-y-3">
            <h3 className="font-medium text-gray-900">Basic Information</h3>
            <div className="grid grid-cols-2 gap-4 text-sm">
              <div>
                <p className="text-gray-500">Allocation ID</p>
                <p className="font-medium">{handover.allocation_id}</p>
              </div>
              <div>
                <p className="text-gray-500">Customer ID</p>
                <p className="font-medium">{handover.customer_id}</p>
              </div>
              <div>
                <p className="text-gray-500">Handover Date</p>
                <p className="font-medium">{formatDate(handover.handover_date)}</p>
              </div>
              {handover.return_date && (
                <div>
                  <p className="text-gray-500">Return Date</p>
                  <p className="font-medium">{formatDate(handover.return_date)}</p>
                </div>
              )}
            </div>
          </div>

          {/* Key Information */}
          <div className="space-y-3 border-t pt-4">
            <h3 className="font-medium text-gray-900">Key Information</h3>
            <div className="grid grid-cols-2 gap-4">
              <Card className="bg-green-50">
                <CardContent className="pt-6">
                  <div className="flex items-center gap-3 mb-3">
                    <Key className="h-5 w-5 text-green-600" />
                    <h4 className="font-medium text-green-900">Customer Key</h4>
                  </div>
                  <p className="text-lg font-bold text-green-900">{handover.customer_key_number}</p>
                  {handover.key_tested && (
                    <p className="text-xs text-green-700 mt-2 flex items-center gap-1">
                      <CheckCircle className="h-3 w-3" />
                      Tested
                    </p>
                  )}
                </CardContent>
              </Card>

              <Card className="bg-purple-50">
                <CardContent className="pt-6">
                  <div className="flex items-center gap-3 mb-3">
                    <Shield className="h-5 w-5 text-purple-600" />
                    <h4 className="font-medium text-purple-900">Bank Master Key</h4>
                  </div>
                  <p className="text-lg font-bold text-purple-900">{handover.bank_key_number}</p>
                  {handover.bank_key_location && (
                    <p className="text-xs text-purple-700 mt-2">
                      Location: {handover.bank_key_location}
                    </p>
                  )}
                </CardContent>
              </Card>
            </div>
          </div>

          {/* Witness Information */}
          {handover.witness_name && (
            <div className="space-y-3 border-t pt-4">
              <h3 className="font-medium text-gray-900">Witness Information</h3>
              <div className="grid grid-cols-2 gap-4 text-sm">
                <div>
                  <p className="text-gray-500">Witness Name</p>
                  <p className="font-medium">{handover.witness_name}</p>
                </div>
                <div>
                  <p className="text-gray-500">Witness ID</p>
                  <p className="font-medium">{handover.witness_id}</p>
                </div>
              </div>
            </div>
          )}

          {/* Verification Status */}
          <div className="space-y-3 border-t pt-4">
            <h3 className="font-medium text-gray-900">Verification Status</h3>
            <div className="grid grid-cols-2 gap-3">
              <div className={`p-3 rounded-lg ${handover.biometric_captured ? 'bg-green-50' : 'bg-gray-50'}`}>
                <div className="flex items-center gap-2">
                  <Fingerprint className={`h-4 w-4 ${handover.biometric_captured ? 'text-green-600' : 'text-gray-400'}`} />
                  <span className="text-sm font-medium">Biometric</span>
                </div>
                <p className="text-xs mt-1 text-gray-600">
                  {handover.biometric_captured ? 'Captured' : 'Not Captured'}
                </p>
              </div>

              <div className={`p-3 rounded-lg ${handover.key_tested ? 'bg-green-50' : 'bg-gray-50'}`}>
                <div className="flex items-center gap-2">
                  <Key className={`h-4 w-4 ${handover.key_tested ? 'text-green-600' : 'text-gray-400'}`} />
                  <span className="text-sm font-medium">Key Tested</span>
                </div>
                <p className="text-xs mt-1 text-gray-600">
                  {handover.key_tested ? 'Verified' : 'Not Tested'}
                </p>
              </div>

              <div className={`p-3 rounded-lg ${handover.lock_tested ? 'bg-green-50' : 'bg-gray-50'}`}>
                <div className="flex items-center gap-2">
                  <CheckCircle className={`h-4 w-4 ${handover.lock_tested ? 'text-green-600' : 'text-gray-400'}`} />
                  <span className="text-sm font-medium">Lock Tested</span>
                </div>
                <p className="text-xs mt-1 text-gray-600">
                  {handover.lock_tested ? 'Verified' : 'Not Tested'}
                </p>
              </div>

              <div className={`p-3 rounded-lg ${handover.dual_key_available ? 'bg-green-50' : 'bg-gray-50'}`}>
                <div className="flex items-center gap-2">
                  <Shield className={`h-4 w-4 ${handover.dual_key_available ? 'text-green-600' : 'text-gray-400'}`} />
                  <span className="text-sm font-medium">Dual Key</span>
                </div>
                <p className="text-xs mt-1 text-gray-600">
                  {handover.dual_key_available ? 'Available' : 'Unavailable'}
                </p>
              </div>
            </div>
          </div>

          {/* Lost Key Details */}
          {handover.key_status === KeyStatus.LOST && handover.lost_key_details && (
            <div className="space-y-3 border-t pt-4">
              <h3 className="font-medium text-gray-900">Lost Key Details</h3>
              <div className="bg-red-50 rounded-lg p-4 space-y-3">
                <div className="grid grid-cols-2 gap-4 text-sm">
                  {handover.lost_key_details.lost_date && (
                    <div>
                      <p className="text-gray-600">Lost Date</p>
                      <p className="font-medium">{formatDate(handover.lost_key_details.lost_date)}</p>
                    </div>
                  )}
                  {handover.lost_key_details.lost_key_type && (
                    <div>
                      <p className="text-gray-600">Lost Key Type</p>
                      <p className="font-medium">{handover.lost_key_details.lost_key_type}</p>
                    </div>
                  )}
                  {handover.lost_key_details.fir_number && (
                    <div>
                      <p className="text-gray-600">FIR Number</p>
                      <p className="font-medium">{handover.lost_key_details.fir_number}</p>
                    </div>
                  )}
                  {handover.lost_key_details.duplicate_key_charges && (
                    <div>
                      <p className="text-gray-600">Duplicate Charges</p>
                      <p className="font-medium">{formatCurrency(handover.lost_key_details.duplicate_key_charges)}</p>
                    </div>
                  )}
                </div>
                {handover.lost_key_details.indemnity_bond_received && (
                  <div className="flex items-center gap-2 text-sm text-green-700">
                    <CheckCircle className="h-4 w-4" />
                    <span>Indemnity Bond Received</span>
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Remarks */}
          {handover.remarks && (
            <div className="space-y-2 border-t pt-4">
              <h3 className="font-medium text-gray-900">Remarks</h3>
              <p className="text-sm text-gray-700 bg-gray-50 rounded-lg p-3">
                {handover.remarks}
              </p>
            </div>
          )}

          {/* Timeline */}
          <div className="space-y-3 border-t pt-4">
            <h3 className="font-medium text-gray-900">Timeline</h3>
            <div className="space-y-2">
              <div className="flex items-center gap-3 text-sm">
                <div className="w-2 h-2 rounded-full bg-green-500"></div>
                <div className="flex-1">
                  <p className="font-medium">Keys Issued</p>
                  <p className="text-xs text-gray-500">{formatDate(handover.handover_date)}</p>
                </div>
              </div>
              {handover.return_date && (
                <div className="flex items-center gap-3 text-sm">
                  <div className="w-2 h-2 rounded-full bg-blue-500"></div>
                  <div className="flex-1">
                    <p className="font-medium">Keys Returned</p>
                    <p className="text-xs text-gray-500">{formatDate(handover.return_date)}</p>
                  </div>
                </div>
              )}
              {handover.key_status === KeyStatus.LOST && handover.lost_key_details?.lost_date && (
                <div className="flex items-center gap-3 text-sm">
                  <div className="w-2 h-2 rounded-full bg-red-500"></div>
                  <div className="flex-1">
                    <p className="font-medium">Key Lost Reported</p>
                    <p className="text-xs text-gray-500">{formatDate(handover.lost_key_details.lost_date)}</p>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>

        <DialogFooter>
          <Button variant="outline" onClick={() => onOpenChange(false)}>
            Close
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}
