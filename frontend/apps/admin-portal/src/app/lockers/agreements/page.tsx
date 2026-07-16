'use client'

import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { 
  FileText, Plus, Search, Filter, Eye, Edit, CheckCircle, 
  XCircle, Clock, AlertTriangle, RefreshCw, Send, FileSignature, Users
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
import { 
  agreementService, 
  AgreementStatus,
  AgreementType,
  SignatureType,
  type LockerAgreement 
} from '@/services/locker.service'
import { formatCurrency, formatDate } from '@/lib/utils'
import { toast } from 'sonner'

export default function AgreementsPage() {
  const [page, setPage] = useState(1)
  const [search, setSearch] = useState('')
  const [statusFilter, setStatusFilter] = useState<AgreementStatus | ''>('')
  const [typeFilter, setTypeFilter] = useState<AgreementType | ''>('')
  const [isCreateOpen, setIsCreateOpen] = useState(false)
  const [isSignOpen, setIsSignOpen] = useState(false)
  const [isExecuteOpen, setIsExecuteOpen] = useState(false)
  const [isRenewOpen, setIsRenewOpen] = useState(false)
  const [isTerminateOpen, setIsTerminateOpen] = useState(false)
  const [isViewOpen, setIsViewOpen] = useState(false)
  const [selectedAgreement, setSelectedAgreement] = useState<LockerAgreement | null>(null)
  const [activeTab, setActiveTab] = useState('all')

  const queryClient = useQueryClient()

  const { data, isLoading } = useQuery({
    queryKey: ['agreements', page, search, statusFilter, typeFilter, activeTab],
    queryFn: () => {
      const params: any = {
        skip: (page - 1) * 12,
        limit: 12,
      }
      if (statusFilter) params.status = statusFilter
      if (typeFilter) params.agreement_type = typeFilter
      if (activeTab === 'active') params.status = AgreementStatus.ACTIVE
      if (activeTab === 'expiring') params.expiring_within_days = 60
      if (activeTab === 'pending-signatures') params.status = AgreementStatus.PENDING_SIGNATURES
      return agreementService.listAgreements(params)
    },
  })

  const { data: statisticsData } = useQuery({
    queryKey: ['agreement-statistics'],
    queryFn: () => agreementService.getStatistics(),
  })

  const { data: expiringData } = useQuery({
    queryKey: ['agreements-expiring'],
    queryFn: () => agreementService.getExpiringAgreements(60),
  })

  const { data: pendingSignaturesData } = useQuery({
    queryKey: ['agreements-pending-signatures'],
    queryFn: () => agreementService.getPendingSignatures(),
  })

  const createMutation = useMutation({
    mutationFn: (data: any) => agreementService.createAgreement(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['agreements'] })
      setIsCreateOpen(false)
      toast.success('Agreement created successfully')
    },
    onError: () => {
      toast.error('Failed to create agreement')
    },
  })

  const signMutation = useMutation({
    mutationFn: ({ id, data }: { id: string; data: any }) =>
      agreementService.addSignature(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['agreements'] })
      queryClient.invalidateQueries({ queryKey: ['agreements-pending-signatures'] })
      setIsSignOpen(false)
      toast.success('Signature added successfully')
    },
    onError: () => {
      toast.error('Failed to add signature')
    },
  })

  const executeMutation = useMutation({
    mutationFn: ({ id, data }: { id: string; data: any }) =>
      agreementService.executeAgreement(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['agreements'] })
      setIsExecuteOpen(false)
      toast.success('Agreement executed successfully')
    },
    onError: () => {
      toast.error('Failed to execute agreement')
    },
  })

  const renewMutation = useMutation({
    mutationFn: ({ id, data }: { id: string; data: any }) =>
      agreementService.renewAgreement(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['agreements'] })
      setIsRenewOpen(false)
      toast.success('Agreement renewed successfully')
    },
    onError: () => {
      toast.error('Failed to renew agreement')
    },
  })

  const terminateMutation = useMutation({
    mutationFn: ({ id, data }: { id: string; data: any }) =>
      agreementService.terminateAgreement(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['agreements'] })
      setIsTerminateOpen(false)
      toast.success('Agreement terminated successfully')
    },
    onError: () => {
      toast.error('Failed to terminate agreement')
    },
  })

  const getStatusColor = (status: AgreementStatus) => {
    const colors = {
      draft: 'bg-gray-100 text-gray-800',
      pending_signatures: 'bg-yellow-100 text-yellow-800',
      active: 'bg-green-100 text-green-800',
      expired: 'bg-red-100 text-red-800',
      terminated: 'bg-orange-100 text-orange-800',
      renewed: 'bg-blue-100 text-blue-800',
    }
    return colors[status] || 'bg-gray-100 text-gray-800'
  }

  const handleView = (agreement: LockerAgreement) => {
    setSelectedAgreement(agreement)
    setIsViewOpen(true)
  }

  const handleSign = (agreement: LockerAgreement) => {
    setSelectedAgreement(agreement)
    setIsSignOpen(true)
  }

  const handleExecute = (agreement: LockerAgreement) => {
    setSelectedAgreement(agreement)
    setIsExecuteOpen(true)
  }

  const handleRenew = (agreement: LockerAgreement) => {
    setSelectedAgreement(agreement)
    setIsRenewOpen(true)
  }

  const handleTerminate = (agreement: LockerAgreement) => {
    setSelectedAgreement(agreement)
    setIsTerminateOpen(true)
  }

  return (
    <DashboardLayout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Locker Agreements</h1>
            <p className="text-gray-600 mt-1">Manage agreements and digital signatures</p>
          </div>
          <Button onClick={() => setIsCreateOpen(true)}>
            <Plus className="h-4 w-4 mr-2" />
            New Agreement
          </Button>
        </div>

        {/* Statistics Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <Card className="border-l-4 border-l-green-500">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Active Agreements</CardTitle>
              <FileText className="h-4 w-4 text-green-600" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-green-600">
                {statisticsData?.data?.active_agreements || 0}
              </div>
              <p className="text-xs text-gray-600 mt-1">Currently valid</p>
            </CardContent>
          </Card>

          <Card className="border-l-4 border-l-yellow-500">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Pending Signatures</CardTitle>
              <FileSignature className="h-4 w-4 text-yellow-600" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-yellow-600">
                {pendingSignaturesData?.data?.pending_signatures?.length || 0}
              </div>
              <p className="text-xs text-gray-600 mt-1">Awaiting signing</p>
            </CardContent>
          </Card>

          <Card className="border-l-4 border-l-orange-500">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Expiring Soon</CardTitle>
              <Clock className="h-4 w-4 text-orange-600" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-orange-600">
                {expiringData?.data?.expiring_agreements?.length || 0}
              </div>
              <p className="text-xs text-gray-600 mt-1">Within 60 days</p>
            </CardContent>
          </Card>

          <Card className="border-l-4 border-l-blue-500">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Total Agreements</CardTitle>
              <Users className="h-4 w-4 text-blue-600" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-blue-600">
                {statisticsData?.data?.total_agreements || 0}
              </div>
              <p className="text-xs text-gray-600 mt-1">All time</p>
            </CardContent>
          </Card>
        </div>

        {/* Tabs */}
        <Tabs value={activeTab} onValueChange={setActiveTab}>
          <TabsList>
            <TabsTrigger value="all">All Agreements</TabsTrigger>
            <TabsTrigger value="active">Active</TabsTrigger>
            <TabsTrigger value="pending-signatures">Pending Signatures</TabsTrigger>
            <TabsTrigger value="expiring">Expiring Soon</TabsTrigger>
          </TabsList>

          <TabsContent value={activeTab} className="space-y-4">
            {/* Filters */}
            <div className="flex items-center gap-4">
              <div className="flex-1 relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
                <Input
                  type="search"
                  placeholder="Search by agreement number, allocation..."
                  className="pl-10"
                  value={search}
                  onChange={(e) => setSearch(e.target.value)}
                />
              </div>
              <Select value={statusFilter} onValueChange={(value) => setStatusFilter(value as AgreementStatus | '')}>
                <SelectTrigger className="w-[200px]">
                  <SelectValue placeholder="All Status" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="">All Status</SelectItem>
                  <SelectItem value={AgreementStatus.DRAFT}>Draft</SelectItem>
                  <SelectItem value={AgreementStatus.PENDING_SIGNATURES}>Pending Signatures</SelectItem>
                  <SelectItem value={AgreementStatus.ACTIVE}>Active</SelectItem>
                  <SelectItem value={AgreementStatus.EXPIRED}>Expired</SelectItem>
                  <SelectItem value={AgreementStatus.TERMINATED}>Terminated</SelectItem>
                </SelectContent>
              </Select>
              <Select value={typeFilter} onValueChange={(value) => setTypeFilter(value as AgreementType | '')}>
                <SelectTrigger className="w-[180px]">
                  <SelectValue placeholder="All Types" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="">All Types</SelectItem>
                  <SelectItem value={AgreementType.NEW}>New</SelectItem>
                  <SelectItem value={AgreementType.RENEWAL}>Renewal</SelectItem>
                  <SelectItem value={AgreementType.AMENDMENT}>Amendment</SelectItem>
                </SelectContent>
              </Select>
            </div>

            {/* Agreements Table */}
            <Card>
              <CardContent className="p-0">
                <div className="overflow-x-auto">
                  <table className="w-full">
                    <thead className="bg-gray-50 border-b">
                      <tr>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                          Agreement
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
                          Signatures
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
                      ) : data?.data?.agreements && data.data.agreements.length > 0 ? (
                        data.data.agreements.map((agreement: LockerAgreement) => (
                          <tr key={agreement.id} className="hover:bg-gray-50">
                            <td className="px-6 py-4 whitespace-nowrap">
                              <div className="text-sm font-medium text-gray-900">
                                {agreement.agreement_number}
                              </div>
                              <div className="text-xs text-gray-500">
                                Type: {agreement.agreement_type}
                              </div>
                            </td>
                            <td className="px-6 py-4">
                              <div className="text-sm text-gray-900">
                                ID: {agreement.customer_id}
                              </div>
                              <div className="text-xs text-gray-500">
                                Alloc: {agreement.allocation_id}
                              </div>
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap">
                              <div className="text-sm text-gray-900">
                                {formatDate(agreement.start_date)}
                              </div>
                              <div className="text-xs text-gray-500">
                                to {formatDate(agreement.end_date)}
                              </div>
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap">
                              <div className="text-sm font-medium text-gray-900">
                                {formatCurrency(agreement.annual_rent)}/yr
                              </div>
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap">
                              <div className="flex items-center gap-1">
                                {agreement.all_signatures_completed ? (
                                  <Badge className="bg-green-100 text-green-800 text-xs">
                                    <CheckCircle className="h-3 w-3 mr-1" />
                                    Complete
                                  </Badge>
                                ) : (
                                  <Badge variant="outline" className="text-xs">
                                    {agreement.signatures_collected || 0}/{agreement.signatures_required || 0}
                                  </Badge>
                                )}
                              </div>
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap">
                              <Badge className={getStatusColor(agreement.status)}>
                                {agreement.status.replace('_', ' ').toUpperCase()}
                              </Badge>
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap text-right">
                              <div className="flex items-center justify-end gap-2">
                                <Button
                                  variant="ghost"
                                  size="sm"
                                  onClick={() => handleView(agreement)}
                                >
                                  <Eye className="h-4 w-4" />
                                </Button>
                                {agreement.status === AgreementStatus.PENDING_SIGNATURES && (
                                  <Button
                                    variant="ghost"
                                    size="sm"
                                    className="text-blue-600"
                                    onClick={() => handleSign(agreement)}
                                  >
                                    <FileSignature className="h-4 w-4" />
                                  </Button>
                                )}
                                {agreement.status === AgreementStatus.PENDING_SIGNATURES && 
                                 agreement.all_signatures_completed && (
                                  <Button
                                    variant="ghost"
                                    size="sm"
                                    className="text-green-600"
                                    onClick={() => handleExecute(agreement)}
                                  >
                                    <CheckCircle className="h-4 w-4" />
                                  </Button>
                                )}
                                {agreement.status === AgreementStatus.ACTIVE && (
                                  <>
                                    <Button
                                      variant="ghost"
                                      size="sm"
                                      className="text-purple-600"
                                      onClick={() => handleRenew(agreement)}
                                    >
                                      <RefreshCw className="h-4 w-4" />
                                    </Button>
                                    <Button
                                      variant="ghost"
                                      size="sm"
                                      className="text-red-600"
                                      onClick={() => handleTerminate(agreement)}
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
                          <td colSpan={7} className="px-6 py-12 text-center text-gray-500">
                            No agreements found
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
        <CreateAgreementDialog
          open={isCreateOpen}
          onOpenChange={setIsCreateOpen}
          onSubmit={(data) => createMutation.mutate(data)}
          isLoading={createMutation.isPending}
        />

        {selectedAgreement && (
          <>
            <AddSignatureDialog
              open={isSignOpen}
              onOpenChange={setIsSignOpen}
              agreement={selectedAgreement}
              onSubmit={(data) => signMutation.mutate({ id: selectedAgreement.id, data })}
              isLoading={signMutation.isPending}
            />
            <ExecuteAgreementDialog
              open={isExecuteOpen}
              onOpenChange={setIsExecuteOpen}
              agreement={selectedAgreement}
              onSubmit={(data) => executeMutation.mutate({ id: selectedAgreement.id, data })}
              isLoading={executeMutation.isPending}
            />
            <RenewAgreementDialog
              open={isRenewOpen}
              onOpenChange={setIsRenewOpen}
              agreement={selectedAgreement}
              onSubmit={(data) => renewMutation.mutate({ id: selectedAgreement.id, data })}
              isLoading={renewMutation.isPending}
            />
            <TerminateAgreementDialog
              open={isTerminateOpen}
              onOpenChange={setIsTerminateOpen}
              agreement={selectedAgreement}
              onSubmit={(data) => terminateMutation.mutate({ id: selectedAgreement.id, data })}
              isLoading={terminateMutation.isPending}
            />
            <ViewAgreementDialog
              open={isViewOpen}
              onOpenChange={setIsViewOpen}
              agreement={selectedAgreement}
            />
          </>
        )}
      </div>
    </DashboardLayout>
  )
}

// Create Agreement Dialog Component
function CreateAgreementDialog({
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
    agreement_number: '',
    agreement_type: AgreementType.NEW,
    allocation_id: '',
    customer_id: '',
    start_date: new Date().toISOString().split('T')[0],
    end_date: '',
    annual_rent: 0,
    security_deposit: 0,
    template_id: '',
    auto_renewal_enabled: false,
    notice_period_days: 30,
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
          <DialogTitle>Create New Agreement</DialogTitle>
          <DialogDescription>Create a locker rental agreement</DialogDescription>
        </DialogHeader>

        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Basic Information */}
          <div className="space-y-4">
            <h3 className="text-sm font-medium">Basic Information</h3>
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="agreement_number">Agreement Number *</Label>
                <Input
                  id="agreement_number"
                  value={formData.agreement_number}
                  onChange={(e) => setFormData({ ...formData, agreement_number: e.target.value })}
                  required
                  placeholder="AUTO-GENERATED"
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="agreement_type">Agreement Type *</Label>
                <Select
                  value={formData.agreement_type}
                  onValueChange={(value) => setFormData({ ...formData, agreement_type: value as AgreementType })}
                >
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value={AgreementType.NEW}>New</SelectItem>
                    <SelectItem value={AgreementType.RENEWAL}>Renewal</SelectItem>
                    <SelectItem value={AgreementType.AMENDMENT}>Amendment</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>

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
            </div>
          </div>

          {/* Agreement Period */}
          <div className="space-y-4 border-t pt-4">
            <h3 className="text-sm font-medium">Agreement Period</h3>
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="start_date">Start Date *</Label>
                <Input
                  id="start_date"
                  type="date"
                  value={formData.start_date}
                  onChange={(e) => setFormData({ ...formData, start_date: e.target.value })}
                  required
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="end_date">End Date *</Label>
                <Input
                  id="end_date"
                  type="date"
                  value={formData.end_date}
                  onChange={(e) => setFormData({ ...formData, end_date: e.target.value })}
                  required
                />
              </div>
            </div>
          </div>

          {/* Financial Terms */}
          <div className="space-y-4 border-t pt-4">
            <h3 className="text-sm font-medium">Financial Terms</h3>
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="annual_rent">Annual Rent (₹) *</Label>
                <Input
                  id="annual_rent"
                  type="number"
                  min="0"
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
                  min="0"
                  value={formData.security_deposit}
                  onChange={(e) => setFormData({ ...formData, security_deposit: parseFloat(e.target.value) })}
                  required
                />
              </div>
            </div>
          </div>

          {/* Agreement Settings */}
          <div className="space-y-4 border-t pt-4">
            <h3 className="text-sm font-medium">Agreement Settings</h3>
            
            <div className="space-y-2">
              <Label htmlFor="template_id">Template</Label>
              <Select
                value={formData.template_id}
                onValueChange={(value) => setFormData({ ...formData, template_id: value })}
              >
                <SelectTrigger>
                  <SelectValue placeholder="Select template" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="standard">Standard Agreement</SelectItem>
                  <SelectItem value="premium">Premium Agreement</SelectItem>
                  <SelectItem value="corporate">Corporate Agreement</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-2">
              <Label htmlFor="notice_period_days">Notice Period (Days)</Label>
              <Input
                id="notice_period_days"
                type="number"
                min="0"
                value={formData.notice_period_days}
                onChange={(e) => setFormData({ ...formData, notice_period_days: parseInt(e.target.value) })}
              />
            </div>

            <div className="flex items-center space-x-2">
              <input
                type="checkbox"
                id="auto_renewal_enabled"
                checked={formData.auto_renewal_enabled}
                onChange={(e) => setFormData({ ...formData, auto_renewal_enabled: e.target.checked })}
                className="rounded"
              />
              <Label htmlFor="auto_renewal_enabled" className="cursor-pointer">
                Enable Auto-Renewal
              </Label>
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
              {isLoading ? 'Creating...' : 'Create Agreement'}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  )
}

// Add Signature Dialog Component
function AddSignatureDialog({
  open,
  onOpenChange,
  agreement,
  onSubmit,
  isLoading,
}: {
  open: boolean
  onOpenChange: (open: boolean) => void
  agreement: LockerAgreement
  onSubmit: (data: any) => void
  isLoading: boolean
}) {
  const [formData, setFormData] = useState({
    signer_type: SignatureType.CUSTOMER,
    signer_name: '',
    signer_id: '',
    signature_date: new Date().toISOString().split('T')[0],
    digital_signature_token: '',
    witness_name: '',
    witness_id: '',
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
          <DialogTitle>Add Digital Signature</DialogTitle>
          <DialogDescription>
            Add signature for agreement {agreement.agreement_number}
          </DialogDescription>
        </DialogHeader>

        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Agreement Summary */}
          <Card className="bg-blue-50 border-blue-200">
            <CardContent className="pt-6">
              <div className="grid grid-cols-2 gap-4 text-sm">
                <div>
                  <p className="text-gray-600">Agreement Number</p>
                  <p className="font-medium">{agreement.agreement_number}</p>
                </div>
                <div>
                  <p className="text-gray-600">Customer ID</p>
                  <p className="font-medium">{agreement.customer_id}</p>
                </div>
                <div>
                  <p className="text-gray-600">Signatures</p>
                  <p className="font-medium">
                    {agreement.signatures_collected || 0} / {agreement.signatures_required || 0}
                  </p>
                </div>
                <div>
                  <p className="text-gray-600">Status</p>
                  <Badge className={getStatusColor(agreement.status)}>
                    {agreement.status}
                  </Badge>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Signer Information */}
          <div className="space-y-4">
            <h3 className="text-sm font-medium">Signer Information</h3>
            
            <div className="space-y-2">
              <Label htmlFor="signer_type">Signer Type *</Label>
              <Select
                value={formData.signer_type}
                onValueChange={(value) => setFormData({ ...formData, signer_type: value as SignatureType })}
              >
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value={SignatureType.CUSTOMER}>Customer</SelectItem>
                  <SelectItem value={SignatureType.JOINT_HOLDER_1}>Joint Holder 1</SelectItem>
                  <SelectItem value={SignatureType.JOINT_HOLDER_2}>Joint Holder 2</SelectItem>
                  <SelectItem value={SignatureType.BANK_OFFICIAL}>Bank Official</SelectItem>
                  <SelectItem value={SignatureType.WITNESS}>Witness</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="signer_name">Signer Name *</Label>
                <Input
                  id="signer_name"
                  value={formData.signer_name}
                  onChange={(e) => setFormData({ ...formData, signer_name: e.target.value })}
                  required
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="signer_id">Signer ID *</Label>
                <Input
                  id="signer_id"
                  value={formData.signer_id}
                  onChange={(e) => setFormData({ ...formData, signer_id: e.target.value })}
                  required
                />
              </div>
            </div>

            <div className="space-y-2">
              <Label htmlFor="signature_date">Signature Date</Label>
              <Input
                id="signature_date"
                type="date"
                value={formData.signature_date}
                onChange={(e) => setFormData({ ...formData, signature_date: e.target.value })}
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="digital_signature_token">Digital Signature Token</Label>
              <Input
                id="digital_signature_token"
                value={formData.digital_signature_token}
                onChange={(e) => setFormData({ ...formData, digital_signature_token: e.target.value })}
                placeholder="Optional: Enter digital signature hash"
              />
              <p className="text-xs text-gray-500">For digital signature verification</p>
            </div>
          </div>

          {/* Witness Information */}
          <div className="space-y-4 border-t pt-4">
            <h3 className="text-sm font-medium">Witness (Optional)</h3>
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="witness_name">Witness Name</Label>
                <Input
                  id="witness_name"
                  value={formData.witness_name}
                  onChange={(e) => setFormData({ ...formData, witness_name: e.target.value })}
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="witness_id">Witness ID</Label>
                <Input
                  id="witness_id"
                  value={formData.witness_id}
                  onChange={(e) => setFormData({ ...formData, witness_id: e.target.value })}
                />
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
              rows={2}
            />
          </div>

          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
            <div className="flex items-start gap-3">
              <FileSignature className="h-5 w-5 text-blue-600 mt-0.5" />
              <div className="text-sm text-blue-900">
                <p className="font-medium mb-1">Digital Signature Process</p>
                <ul className="list-disc list-inside space-y-1 text-blue-800">
                  <li>Verify signer identity before proceeding</li>
                  <li>Ensure signer has reviewed agreement terms</li>
                  <li>Digital signature will be recorded with timestamp</li>
                  <li>Once all signatures collected, agreement can be executed</li>
                </ul>
              </div>
            </div>
          </div>

          <DialogFooter>
            <Button type="button" variant="outline" onClick={() => onOpenChange(false)}>
              Cancel
            </Button>
            <Button type="submit" disabled={isLoading} className="bg-blue-600 hover:bg-blue-700">
              {isLoading ? 'Adding...' : 'Add Signature'}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  )
}

// Execute Agreement Dialog Component
function ExecuteAgreementDialog({
  open,
  onOpenChange,
  agreement,
  onSubmit,
  isLoading,
}: {
  open: boolean
  onOpenChange: (open: boolean) => void
  agreement: LockerAgreement
  onSubmit: (data: any) => void
  isLoading: boolean
}) {
  const [formData, setFormData] = useState({
    execution_date: new Date().toISOString().split('T')[0],
    executed_by: '',
    stamp_paper_value: 0,
    stamp_paper_number: '',
    notary_details: '',
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
          <DialogTitle>Execute Agreement</DialogTitle>
          <DialogDescription>
            Execute agreement {agreement.agreement_number}
          </DialogDescription>
        </DialogHeader>

        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Execution Details */}
          <div className="space-y-4">
            <h3 className="text-sm font-medium">Execution Details</h3>
            
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="execution_date">Execution Date *</Label>
                <Input
                  id="execution_date"
                  type="date"
                  value={formData.execution_date}
                  onChange={(e) => setFormData({ ...formData, execution_date: e.target.value })}
                  required
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="executed_by">Executed By *</Label>
                <Input
                  id="executed_by"
                  value={formData.executed_by}
                  onChange={(e) => setFormData({ ...formData, executed_by: e.target.value })}
                  required
                  placeholder="Official name"
                />
              </div>
            </div>
          </div>

          {/* Stamp Paper Details */}
          <div className="space-y-4 border-t pt-4">
            <h3 className="text-sm font-medium">Stamp Paper Details</h3>
            
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="stamp_paper_value">Stamp Paper Value (₹)</Label>
                <Input
                  id="stamp_paper_value"
                  type="number"
                  min="0"
                  value={formData.stamp_paper_value}
                  onChange={(e) => setFormData({ ...formData, stamp_paper_value: parseFloat(e.target.value) })}
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="stamp_paper_number">Stamp Paper Number</Label>
                <Input
                  id="stamp_paper_number"
                  value={formData.stamp_paper_number}
                  onChange={(e) => setFormData({ ...formData, stamp_paper_number: e.target.value })}
                />
              </div>
            </div>
          </div>

          {/* Notary Details */}
          <div className="space-y-2">
            <Label htmlFor="notary_details">Notary Details (Optional)</Label>
            <Textarea
              id="notary_details"
              value={formData.notary_details}
              onChange={(e) => setFormData({ ...formData, notary_details: e.target.value })}
              placeholder="Notary name, registration number, etc."
              rows={3}
            />
          </div>

          {/* Remarks */}
          <div className="space-y-2">
            <Label htmlFor="remarks">Remarks</Label>
            <Textarea
              id="remarks"
              value={formData.remarks}
              onChange={(e) => setFormData({ ...formData, remarks: e.target.value })}
              placeholder="Any additional notes..."
              rows={2}
            />
          </div>

          <div className="bg-green-50 border border-green-200 rounded-lg p-4">
            <div className="flex items-start gap-3">
              <CheckCircle className="h-5 w-5 text-green-600 mt-0.5" />
              <div className="text-sm text-green-900">
                <p className="font-medium mb-1">Agreement Execution</p>
                <ul className="list-disc list-inside space-y-1 text-green-800">
                  <li>All required signatures must be collected</li>
                  <li>Agreement becomes legally binding upon execution</li>
                  <li>Status will change to ACTIVE</li>
                  <li>Customer and bank copies will be generated</li>
                </ul>
              </div>
            </div>
          </div>

          <DialogFooter>
            <Button type="button" variant="outline" onClick={() => onOpenChange(false)}>
              Cancel
            </Button>
            <Button type="submit" disabled={isLoading} className="bg-green-600 hover:bg-green-700">
              {isLoading ? 'Executing...' : 'Execute Agreement'}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  )
}

// Renew Agreement Dialog Component
function RenewAgreementDialog({
  open,
  onOpenChange,
  agreement,
  onSubmit,
  isLoading,
}: {
  open: boolean
  onOpenChange: (open: boolean) => void
  agreement: LockerAgreement
  onSubmit: (data: any) => void
  isLoading: boolean
}) {
  const [formData, setFormData] = useState({
    new_start_date: '',
    new_end_date: '',
    new_annual_rent: agreement.annual_rent,
    rent_escalation_percentage: 0,
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
          <DialogTitle>Renew Agreement</DialogTitle>
          <DialogDescription>
            Renew agreement {agreement.agreement_number}
          </DialogDescription>
        </DialogHeader>

        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Current Agreement Info */}
          <Card className="bg-purple-50 border-purple-200">
            <CardContent className="pt-6">
              <div className="grid grid-cols-2 gap-4 text-sm">
                <div>
                  <p className="text-gray-600">Current Period</p>
                  <p className="font-medium">
                    {formatDate(agreement.start_date)} - {formatDate(agreement.end_date)}
                  </p>
                </div>
                <div>
                  <p className="text-gray-600">Current Rent</p>
                  <p className="font-medium">{formatCurrency(agreement.annual_rent)}/yr</p>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* New Period */}
          <div className="space-y-4">
            <h3 className="text-sm font-medium">New Agreement Period</h3>
            
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="new_start_date">New Start Date *</Label>
                <Input
                  id="new_start_date"
                  type="date"
                  value={formData.new_start_date}
                  onChange={(e) => setFormData({ ...formData, new_start_date: e.target.value })}
                  required
                />
              </div>
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
            </div>
          </div>

          {/* Rent Details */}
          <div className="space-y-4 border-t pt-4">
            <h3 className="text-sm font-medium">Rent Details</h3>
            
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="rent_escalation_percentage">Escalation (%)</Label>
                <Input
                  id="rent_escalation_percentage"
                  type="number"
                  min="0"
                  max="100"
                  step="0.1"
                  value={formData.rent_escalation_percentage}
                  onChange={(e) => {
                    const escalation = parseFloat(e.target.value)
                    const newRent = agreement.annual_rent * (1 + escalation / 100)
                    setFormData({ 
                      ...formData, 
                      rent_escalation_percentage: escalation,
                      new_annual_rent: newRent
                    })
                  }}
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="new_annual_rent">New Annual Rent (₹) *</Label>
                <Input
                  id="new_annual_rent"
                  type="number"
                  min="0"
                  value={formData.new_annual_rent}
                  onChange={(e) => setFormData({ ...formData, new_annual_rent: parseFloat(e.target.value) })}
                  required
                />
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
              placeholder="Renewal notes..."
              rows={3}
            />
          </div>

          <DialogFooter>
            <Button type="button" variant="outline" onClick={() => onOpenChange(false)}>
              Cancel
            </Button>
            <Button type="submit" disabled={isLoading} className="bg-purple-600 hover:bg-purple-700">
              {isLoading ? 'Renewing...' : 'Renew Agreement'}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  )
}

// Terminate Agreement Dialog Component
function TerminateAgreementDialog({
  open,
  onOpenChange,
  agreement,
  onSubmit,
  isLoading,
}: {
  open: boolean
  onOpenChange: (open: boolean) => void
  agreement: LockerAgreement
  onSubmit: (data: any) => void
  isLoading: boolean
}) {
  const [formData, setFormData] = useState({
    termination_date: new Date().toISOString().split('T')[0],
    termination_reason: '',
    notice_served: false,
    notice_date: '',
    refund_security_deposit: true,
    remarks: '',
  })

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (!formData.termination_reason.trim()) {
      toast.error('Please provide termination reason')
      return
    }
    onSubmit(formData)
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-2xl">
        <DialogHeader>
          <DialogTitle>Terminate Agreement</DialogTitle>
          <DialogDescription>
            Terminate agreement {agreement.agreement_number}
          </DialogDescription>
        </DialogHeader>

        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Agreement Summary */}
          <Card className="bg-red-50 border-red-200">
            <CardContent className="pt-6">
              <div className="grid grid-cols-2 gap-4 text-sm">
                <div>
                  <p className="text-gray-600">Agreement Number</p>
                  <p className="font-medium">{agreement.agreement_number}</p>
                </div>
                <div>
                  <p className="text-gray-600">Customer ID</p>
                  <p className="font-medium">{agreement.customer_id}</p>
                </div>
                <div>
                  <p className="text-gray-600">Period</p>
                  <p className="font-medium">
                    {formatDate(agreement.start_date)} - {formatDate(agreement.end_date)}
                  </p>
                </div>
                <div>
                  <p className="text-gray-600">Notice Period</p>
                  <p className="font-medium">{agreement.notice_period_days} days</p>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Termination Details */}
          <div className="space-y-4">
            <h3 className="text-sm font-medium">Termination Details</h3>
            
            <div className="space-y-2">
              <Label htmlFor="termination_date">Termination Date *</Label>
              <Input
                id="termination_date"
                type="date"
                value={formData.termination_date}
                onChange={(e) => setFormData({ ...formData, termination_date: e.target.value })}
                required
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="termination_reason">Termination Reason *</Label>
              <Textarea
                id="termination_reason"
                value={formData.termination_reason}
                onChange={(e) => setFormData({ ...formData, termination_reason: e.target.value })}
                placeholder="Provide detailed reason for termination..."
                rows={4}
                required
              />
            </div>
          </div>

          {/* Notice Details */}
          <div className="space-y-4 border-t pt-4">
            <h3 className="text-sm font-medium">Notice Details</h3>
            
            <div className="flex items-center space-x-2">
              <input
                type="checkbox"
                id="notice_served"
                checked={formData.notice_served}
                onChange={(e) => setFormData({ ...formData, notice_served: e.target.checked })}
                className="rounded"
              />
              <Label htmlFor="notice_served" className="cursor-pointer">
                Notice Period Served
              </Label>
            </div>

            {formData.notice_served && (
              <div className="space-y-2">
                <Label htmlFor="notice_date">Notice Date</Label>
                <Input
                  id="notice_date"
                  type="date"
                  value={formData.notice_date}
                  onChange={(e) => setFormData({ ...formData, notice_date: e.target.value })}
                />
              </div>
            )}
          </div>

          {/* Refund */}
          <div className="flex items-center space-x-2">
            <input
              type="checkbox"
              id="refund_security_deposit"
              checked={formData.refund_security_deposit}
              onChange={(e) => setFormData({ ...formData, refund_security_deposit: e.target.checked })}
              className="rounded"
            />
            <Label htmlFor="refund_security_deposit" className="cursor-pointer">
              Refund Security Deposit ({formatCurrency(agreement.security_deposit)})
            </Label>
          </div>

          {/* Remarks */}
          <div className="space-y-2">
            <Label htmlFor="remarks">Additional Remarks</Label>
            <Textarea
              id="remarks"
              value={formData.remarks}
              onChange={(e) => setFormData({ ...formData, remarks: e.target.value })}
              placeholder="Any additional notes..."
              rows={2}
            />
          </div>

          {/* Warning */}
          <div className="bg-red-50 border border-red-200 rounded-lg p-4">
            <div className="flex items-start gap-3">
              <AlertTriangle className="h-5 w-5 text-red-600 mt-0.5" />
              <div className="text-sm text-red-900">
                <p className="font-medium mb-1">Termination Consequences</p>
                <ul className="list-disc list-inside space-y-1 text-red-800">
                  <li>Agreement will be terminated immediately</li>
                  <li>Locker must be cleared and keys returned</li>
                  <li>Security deposit will be processed for refund</li>
                  <li>This action cannot be undone</li>
                </ul>
              </div>
            </div>
          </div>

          <DialogFooter>
            <Button type="button" variant="outline" onClick={() => onOpenChange(false)}>
              Cancel
            </Button>
            <Button type="submit" disabled={isLoading} className="bg-red-600 hover:bg-red-700">
              {isLoading ? 'Terminating...' : 'Terminate Agreement'}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  )
}

// View Agreement Dialog Component
function ViewAgreementDialog({
  open,
  onOpenChange,
  agreement,
}: {
  open: boolean
  onOpenChange: (open: boolean) => void
  agreement: LockerAgreement
}) {
  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-4xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>Agreement Details</DialogTitle>
          <DialogDescription>
            Agreement #{agreement.agreement_number}
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-6">
          {/* Status Banner */}
          <div className={`p-4 rounded-lg border-l-4 ${
            agreement.status === AgreementStatus.ACTIVE ? 'bg-green-50 border-green-500' :
            agreement.status === AgreementStatus.PENDING_SIGNATURES ? 'bg-yellow-50 border-yellow-500' :
            agreement.status === AgreementStatus.EXPIRED ? 'bg-red-50 border-red-500' :
            'bg-gray-50 border-gray-500'
          }`}>
            <div className="flex items-center justify-between">
              <div>
                <p className="font-medium">Status: {agreement.status.replace('_', ' ').toUpperCase()}</p>
                <p className="text-sm mt-1">Type: {agreement.agreement_type}</p>
              </div>
              <Badge className={getStatusColor(agreement.status)}>
                {agreement.status.replace('_', ' ').toUpperCase()}
              </Badge>
            </div>
          </div>

          {/* Basic Information */}
          <div className="space-y-3">
            <h3 className="font-medium text-gray-900">Basic Information</h3>
            <div className="grid grid-cols-2 gap-4 text-sm">
              <div>
                <p className="text-gray-500">Agreement Number</p>
                <p className="font-medium">{agreement.agreement_number}</p>
              </div>
              <div>
                <p className="text-gray-500">Agreement Type</p>
                <p className="font-medium">{agreement.agreement_type}</p>
              </div>
              <div>
                <p className="text-gray-500">Customer ID</p>
                <p className="font-medium">{agreement.customer_id}</p>
              </div>
              <div>
                <p className="text-gray-500">Allocation ID</p>
                <p className="font-medium">{agreement.allocation_id}</p>
              </div>
            </div>
          </div>

          {/* Agreement Period */}
          <div className="space-y-3 border-t pt-4">
            <h3 className="font-medium text-gray-900">Agreement Period</h3>
            <div className="grid grid-cols-2 gap-4 text-sm">
              <div>
                <p className="text-gray-500">Start Date</p>
                <p className="font-medium">{formatDate(agreement.start_date)}</p>
              </div>
              <div>
                <p className="text-gray-500">End Date</p>
                <p className="font-medium">{formatDate(agreement.end_date)}</p>
              </div>
              {agreement.execution_date && (
                <div>
                  <p className="text-gray-500">Execution Date</p>
                  <p className="font-medium">{formatDate(agreement.execution_date)}</p>
                </div>
              )}
              <div>
                <p className="text-gray-500">Notice Period</p>
                <p className="font-medium">{agreement.notice_period_days} days</p>
              </div>
            </div>
          </div>

          {/* Financial Terms */}
          <div className="space-y-3 border-t pt-4">
            <h3 className="font-medium text-gray-900">Financial Terms</h3>
            <div className="grid grid-cols-2 gap-4 text-sm">
              <div>
                <p className="text-gray-500">Annual Rent</p>
                <p className="font-medium text-lg">{formatCurrency(agreement.annual_rent)}</p>
              </div>
              <div>
                <p className="text-gray-500">Security Deposit</p>
                <p className="font-medium text-lg">{formatCurrency(agreement.security_deposit)}</p>
              </div>
            </div>
          </div>

          {/* Signatures */}
          <div className="space-y-3 border-t pt-4">
            <h3 className="font-medium text-gray-900">Digital Signatures</h3>
            <div className="flex items-center justify-between mb-3">
              <p className="text-sm text-gray-600">
                Progress: {agreement.signatures_collected || 0} of {agreement.signatures_required || 0} signatures
              </p>
              {agreement.all_signatures_completed ? (
                <Badge className="bg-green-100 text-green-800">
                  <CheckCircle className="h-3 w-3 mr-1" />
                  All Signatures Collected
                </Badge>
              ) : (
                <Badge variant="outline">
                  Pending Signatures
                </Badge>
              )}
            </div>
            
            {agreement.signatures && agreement.signatures.length > 0 ? (
              <div className="space-y-2">
                {agreement.signatures.map((sig: any, index: number) => (
                  <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                    <div className="flex items-center gap-3">
                      <FileSignature className="h-4 w-4 text-blue-600" />
                      <div>
                        <p className="text-sm font-medium">{sig.signer_name}</p>
                        <p className="text-xs text-gray-500">{sig.signer_type}</p>
                      </div>
                    </div>
                    <div className="text-right">
                      <p className="text-xs text-gray-500">{formatDate(sig.signature_date)}</p>
                      {sig.digital_signature_token && (
                        <Badge variant="outline" className="text-xs mt-1">
                          Verified
                        </Badge>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-sm text-gray-500">No signatures recorded yet</p>
            )}
          </div>

          {/* Execution Details */}
          {agreement.execution_details && (
            <div className="space-y-3 border-t pt-4">
              <h3 className="font-medium text-gray-900">Execution Details</h3>
              <div className="bg-green-50 rounded-lg p-4">
                <div className="grid grid-cols-2 gap-4 text-sm">
                  {agreement.execution_details.executed_by && (
                    <div>
                      <p className="text-gray-600">Executed By</p>
                      <p className="font-medium">{agreement.execution_details.executed_by}</p>
                    </div>
                  )}
                  {agreement.execution_details.stamp_paper_value && (
                    <div>
                      <p className="text-gray-600">Stamp Paper Value</p>
                      <p className="font-medium">{formatCurrency(agreement.execution_details.stamp_paper_value)}</p>
                    </div>
                  )}
                  {agreement.execution_details.stamp_paper_number && (
                    <div>
                      <p className="text-gray-600">Stamp Paper Number</p>
                      <p className="font-medium">{agreement.execution_details.stamp_paper_number}</p>
                    </div>
                  )}
                  {agreement.execution_details.notary_details && (
                    <div className="col-span-2">
                      <p className="text-gray-600">Notary Details</p>
                      <p className="font-medium">{agreement.execution_details.notary_details}</p>
                    </div>
                  )}
                </div>
              </div>
            </div>
          )}

          {/* Auto-Renewal */}
          {agreement.auto_renewal_enabled && (
            <div className="border-t pt-4">
              <div className="flex items-center gap-2 text-sm">
                <RefreshCw className="h-4 w-4 text-purple-600" />
                <span className="font-medium text-purple-900">Auto-Renewal Enabled</span>
              </div>
            </div>
          )}

          {/* Remarks */}
          {agreement.remarks && (
            <div className="space-y-2 border-t pt-4">
              <h3 className="font-medium text-gray-900">Remarks</h3>
              <p className="text-sm text-gray-700 bg-gray-50 rounded-lg p-3">
                {agreement.remarks}
              </p>
            </div>
          )}

          {/* Timeline */}
          <div className="space-y-3 border-t pt-4">
            <h3 className="font-medium text-gray-900">Timeline</h3>
            <div className="space-y-2">
              <div className="flex items-center gap-3 text-sm">
                <div className="w-2 h-2 rounded-full bg-blue-500"></div>
                <div className="flex-1">
                  <p className="font-medium">Agreement Created</p>
                  <p className="text-xs text-gray-500">{formatDate(agreement.created_at)}</p>
                </div>
              </div>
              {agreement.execution_date && (
                <div className="flex items-center gap-3 text-sm">
                  <div className="w-2 h-2 rounded-full bg-green-500"></div>
                  <div className="flex-1">
                    <p className="font-medium">Agreement Executed</p>
                    <p className="text-xs text-gray-500">{formatDate(agreement.execution_date)}</p>
                  </div>
                </div>
              )}
              {agreement.status === AgreementStatus.TERMINATED && agreement.termination_date && (
                <div className="flex items-center gap-3 text-sm">
                  <div className="w-2 h-2 rounded-full bg-red-500"></div>
                  <div className="flex-1">
                    <p className="font-medium">Agreement Terminated</p>
                    <p className="text-xs text-gray-500">{formatDate(agreement.termination_date)}</p>
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
          <Button>
            <FileText className="h-4 w-4 mr-2" />
            Download PDF
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}
