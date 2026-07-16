'use client'

import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { 
  Plus, Search, Filter, Eye, FileText, CheckCircle, XCircle, 
  Clock, AlertTriangle, TrendingUp, Users, DollarSign, Upload
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
  applicationService, 
  ApplicationStatus, 
  ApplicationType,
  ApplicationStage,
  type LockerApplication 
} from '@/services/locker.service'
import { formatCurrency, formatDate } from '@/lib/utils'
import { toast } from 'sonner'

export default function ApplicationsPage() {
  const [page, setPage] = useState(1)
  const [search, setSearch] = useState('')
  const [statusFilter, setStatusFilter] = useState<ApplicationStatus | ''>('')
  const [typeFilter, setTypeFilter] = useState<ApplicationType | ''>('')
  const [isCreateOpen, setIsCreateOpen] = useState(false)
  const [isViewOpen, setIsViewOpen] = useState(false)
  const [selectedApplication, setSelectedApplication] = useState<LockerApplication | null>(null)
  const [activeTab, setActiveTab] = useState('all')

  const queryClient = useQueryClient()

  const { data, isLoading } = useQuery({
    queryKey: ['applications', page, search, statusFilter, typeFilter, activeTab],
    queryFn: () => {
      const params: any = {
        skip: (page - 1) * 12,
        limit: 12,
      }
      if (statusFilter) params.status = statusFilter
      if (typeFilter) params.application_type = typeFilter
      if (activeTab === 'pending') params.status = ApplicationStatus.PENDING_REVIEW
      if (activeTab === 'approved') params.status = ApplicationStatus.APPROVED
      return applicationService.listApplications(params)
    },
  })

  const { data: analyticsData } = useQuery({
    queryKey: ['applications-analytics'],
    queryFn: () => applicationService.getAnalytics(),
  })

  const { data: pendingApprovalsData } = useQuery({
    queryKey: ['applications-pending-approvals'],
    queryFn: () => applicationService.getPendingApprovals(),
  })

  const createMutation = useMutation({
    mutationFn: (data: any) => applicationService.createApplication(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['applications'] })
      setIsCreateOpen(false)
      toast.success('Application created successfully')
    },
    onError: () => {
      toast.error('Failed to create application')
    },
  })

  const approveMutation = useMutation({
    mutationFn: ({ id, data }: { id: string; data: any }) =>
      applicationService.approveApplication(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['applications'] })
      toast.success('Application approved successfully')
    },
    onError: () => {
      toast.error('Failed to approve application')
    },
  })

  const getStatusColor = (status: ApplicationStatus) => {
    const colors = {
      draft: 'bg-gray-100 text-gray-800',
      submitted: 'bg-blue-100 text-blue-800',
      pending_review: 'bg-yellow-100 text-yellow-800',
      under_review: 'bg-orange-100 text-orange-800',
      approved: 'bg-green-100 text-green-800',
      rejected: 'bg-red-100 text-red-800',
      allocated: 'bg-purple-100 text-purple-800',
      waitlisted: 'bg-cyan-100 text-cyan-800',
      cancelled: 'bg-gray-100 text-gray-800',
    }
    return colors[status] || 'bg-gray-100 text-gray-800'
  }

  const getTypeColor = (type: ApplicationType) => {
    const colors = {
      new: 'bg-green-100 text-green-800',
      renewal: 'bg-blue-100 text-blue-800',
      transfer: 'bg-orange-100 text-orange-800',
      upgrade: 'bg-purple-100 text-purple-800',
      additional: 'bg-cyan-100 text-cyan-800',
    }
    return colors[type] || 'bg-gray-100 text-gray-800'
  }

  const handleView = (application: LockerApplication) => {
    setSelectedApplication(application)
    setIsViewOpen(true)
  }

  const handleApprove = (application: LockerApplication) => {
    approveMutation.mutate({
      id: application.id,
      data: { remarks: 'Application approved' }
    })
  }

  return (
    <DashboardLayout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Locker Applications</h1>
            <p className="text-gray-600 mt-1">Manage customer locker applications and approvals</p>
          </div>
          <Button onClick={() => setIsCreateOpen(true)}>
            <Plus className="h-4 w-4 mr-2" />
            New Application
          </Button>
        </div>

        {/* Analytics Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <Card className="border-l-4 border-l-blue-500">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Total Applications</CardTitle>
              <FileText className="h-4 w-4 text-blue-600" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-blue-600">
                {analyticsData?.data?.total_applications || 0}
              </div>
              <p className="text-xs text-gray-600 mt-1">All time</p>
            </CardContent>
          </Card>

          <Card className="border-l-4 border-l-yellow-500">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Pending Review</CardTitle>
              <Clock className="h-4 w-4 text-yellow-600" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-yellow-600">
                {pendingApprovalsData?.data?.pending_approvals?.length || 0}
              </div>
              <p className="text-xs text-gray-600 mt-1">Requires action</p>
            </CardContent>
          </Card>

          <Card className="border-l-4 border-l-green-500">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Approved</CardTitle>
              <CheckCircle className="h-4 w-4 text-green-600" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-green-600">
                {analyticsData?.data?.approved_applications || 0}
              </div>
              <p className="text-xs text-gray-600 mt-1">Ready for allocation</p>
            </CardContent>
          </Card>

          <Card className="border-l-4 border-l-purple-500">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Avg Priority Score</CardTitle>
              <TrendingUp className="h-4 w-4 text-purple-600" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-purple-600">
                {analyticsData?.data?.average_priority_score?.toFixed(1) || '0.0'}
              </div>
              <p className="text-xs text-gray-600 mt-1">Out of 100</p>
            </CardContent>
          </Card>
        </div>

        {/* Tabs */}
        <Tabs value={activeTab} onValueChange={setActiveTab}>
          <TabsList>
            <TabsTrigger value="all">All Applications</TabsTrigger>
            <TabsTrigger value="pending">Pending Review</TabsTrigger>
            <TabsTrigger value="approved">Approved</TabsTrigger>
          </TabsList>

          <TabsContent value={activeTab} className="space-y-4">
            {/* Filters */}
            <div className="flex items-center gap-4">
              <div className="flex-1 relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
                <Input
                  type="search"
                  placeholder="Search by application number, customer ID..."
                  className="pl-10"
                  value={search}
                  onChange={(e) => setSearch(e.target.value)}
                />
              </div>
              <Select value={statusFilter} onValueChange={(value) => setStatusFilter(value as ApplicationStatus | '')}>
                <SelectTrigger className="w-[200px]">
                  <SelectValue placeholder="All Status" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="">All Status</SelectItem>
                  <SelectItem value={ApplicationStatus.SUBMITTED}>Submitted</SelectItem>
                  <SelectItem value={ApplicationStatus.PENDING_REVIEW}>Pending Review</SelectItem>
                  <SelectItem value={ApplicationStatus.APPROVED}>Approved</SelectItem>
                  <SelectItem value={ApplicationStatus.REJECTED}>Rejected</SelectItem>
                  <SelectItem value={ApplicationStatus.ALLOCATED}>Allocated</SelectItem>
                </SelectContent>
              </Select>
              <Select value={typeFilter} onValueChange={(value) => setTypeFilter(value as ApplicationType | '')}>
                <SelectTrigger className="w-[180px]">
                  <SelectValue placeholder="All Types" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="">All Types</SelectItem>
                  <SelectItem value={ApplicationType.NEW}>New</SelectItem>
                  <SelectItem value={ApplicationType.RENEWAL}>Renewal</SelectItem>
                  <SelectItem value={ApplicationType.TRANSFER}>Transfer</SelectItem>
                  <SelectItem value={ApplicationType.UPGRADE}>Upgrade</SelectItem>
                </SelectContent>
              </Select>
            </div>

            {/* Applications Table */}
            <Card>
              <CardContent className="p-0">
                <div className="overflow-x-auto">
                  <table className="w-full">
                    <thead className="bg-gray-50 border-b">
                      <tr>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                          Application
                        </th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                          Customer
                        </th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                          Type
                        </th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                          Preferences
                        </th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                          Priority
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
                            <td className="px-6 py-4"><Skeleton className="h-4 w-24" /></td>
                            <td className="px-6 py-4"><Skeleton className="h-4 w-32" /></td>
                            <td className="px-6 py-4"><Skeleton className="h-4 w-16" /></td>
                            <td className="px-6 py-4"><Skeleton className="h-6 w-24" /></td>
                            <td className="px-6 py-4"><Skeleton className="h-8 w-24" /></td>
                          </tr>
                        ))
                      ) : data?.data?.applications && data.data.applications.length > 0 ? (
                        data.data.applications.map((application: LockerApplication) => (
                          <tr key={application.id} className="hover:bg-gray-50">
                            <td className="px-6 py-4 whitespace-nowrap">
                              <div className="text-sm font-medium text-gray-900">
                                {application.application_number}
                              </div>
                              <div className="text-sm text-gray-500">
                                {formatDate(application.application_date)}
                              </div>
                            </td>
                            <td className="px-6 py-4">
                              <div className="text-sm text-gray-900">
                                ID: {application.customer_id}
                              </div>
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap">
                              <Badge className={getTypeColor(application.application_type)}>
                                {application.application_type.toUpperCase()}
                              </Badge>
                            </td>
                            <td className="px-6 py-4">
                              <div className="text-sm text-gray-900">
                                Size: {application.preferred_size}
                              </div>
                              {application.preferred_location && (
                                <div className="text-xs text-gray-500">
                                  Location: {application.preferred_location}
                                </div>
                              )}
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap">
                              <div className="text-sm font-medium text-gray-900">
                                {application.priority_score || 0}
                              </div>
                              <div className="text-xs text-gray-500">/ 100</div>
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap">
                              <Badge className={getStatusColor(application.status)}>
                                {application.status.replace('_', ' ').toUpperCase()}
                              </Badge>
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap text-right">
                              <div className="flex items-center justify-end gap-2">
                                <Button
                                  variant="ghost"
                                  size="sm"
                                  onClick={() => handleView(application)}
                                >
                                  <Eye className="h-4 w-4" />
                                </Button>
                                {application.status === ApplicationStatus.PENDING_REVIEW && (
                                  <Button
                                    variant="ghost"
                                    size="sm"
                                    className="text-green-600"
                                    onClick={() => handleApprove(application)}
                                  >
                                    <CheckCircle className="h-4 w-4" />
                                  </Button>
                                )}
                              </div>
                            </td>
                          </tr>
                        ))
                      ) : (
                        <tr>
                          <td colSpan={7} className="px-6 py-12 text-center text-gray-500">
                            No applications found
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
        <ApplicationFormDialog
          open={isCreateOpen}
          onOpenChange={setIsCreateOpen}
          onSubmit={(data) => createMutation.mutate(data)}
          isLoading={createMutation.isPending}
        />

        {selectedApplication && (
          <ApplicationViewDialog
            open={isViewOpen}
            onOpenChange={setIsViewOpen}
            application={selectedApplication}
          />
        )}
      </div>
    </DashboardLayout>
  )
}

// Application Form Dialog Component
function ApplicationFormDialog({
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
  const [currentStep, setCurrentStep] = useState(1)
  const [formData, setFormData] = useState<any>({
    application_number: '',
    application_type: ApplicationType.NEW,
    customer_id: '',
    application_date: new Date().toISOString().split('T')[0],
    preferred_size: 'small',
    preferred_location: '',
    alternate_size: '',
    purpose: '',
    expected_usage_frequency: 'weekly',
    joint_holder_1_id: '',
    joint_holder_2_id: '',
    advance_rent_years: 0,
    documents: [],
    kyc_verified: false,
    remarks: '',
  })

  const handleNext = () => {
    if (currentStep < 4) setCurrentStep(currentStep + 1)
  }

  const handlePrevious = () => {
    if (currentStep > 1) setCurrentStep(currentStep - 1)
  }

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    onSubmit(formData)
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-4xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>New Locker Application</DialogTitle>
          <DialogDescription>Fill in the application details (Step {currentStep} of 4)</DialogDescription>
        </DialogHeader>

        {/* Progress Indicator */}
        <div className="flex items-center justify-between mb-6">
          {[1, 2, 3, 4].map((step) => (
            <div key={step} className="flex items-center flex-1">
              <div
                className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-medium ${
                  step <= currentStep
                    ? 'bg-blue-600 text-white'
                    : 'bg-gray-200 text-gray-600'
                }`}
              >
                {step}
              </div>
              {step < 4 && (
                <div
                  className={`flex-1 h-1 mx-2 ${
                    step < currentStep ? 'bg-blue-600' : 'bg-gray-200'
                  }`}
                />
              )}
            </div>
          ))}
        </div>

        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Step 1: Basic Information */}
          {currentStep === 1 && (
            <div className="space-y-4">
              <h3 className="text-lg font-medium">Basic Information</h3>
              
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="application_number">Application Number *</Label>
                  <Input
                    id="application_number"
                    value={formData.application_number}
                    onChange={(e) => setFormData({ ...formData, application_number: e.target.value })}
                    required
                    placeholder="AUTO-GENERATED"
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="application_type">Application Type *</Label>
                  <Select
                    value={formData.application_type}
                    onValueChange={(value) => setFormData({ ...formData, application_type: value as ApplicationType })}
                  >
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value={ApplicationType.NEW}>New Locker</SelectItem>
                      <SelectItem value={ApplicationType.RENEWAL}>Renewal</SelectItem>
                      <SelectItem value={ApplicationType.TRANSFER}>Transfer</SelectItem>
                      <SelectItem value={ApplicationType.UPGRADE}>Upgrade</SelectItem>
                      <SelectItem value={ApplicationType.ADDITIONAL}>Additional</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>

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
                  <Label htmlFor="application_date">Application Date</Label>
                  <Input
                    id="application_date"
                    type="date"
                    value={formData.application_date}
                    onChange={(e) => setFormData({ ...formData, application_date: e.target.value })}
                  />
                </div>
              </div>

              <div className="space-y-2">
                <Label htmlFor="purpose">Purpose of Locker *</Label>
                <Textarea
                  id="purpose"
                  value={formData.purpose}
                  onChange={(e) => setFormData({ ...formData, purpose: e.target.value })}
                  required
                  placeholder="Describe the purpose for renting the locker..."
                  rows={3}
                />
              </div>
            </div>
          )}

          {/* Step 2: Locker Preferences */}
          {currentStep === 2 && (
            <div className="space-y-4">
              <h3 className="text-lg font-medium">Locker Preferences</h3>
              
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="preferred_size">Preferred Size *</Label>
                  <Select
                    value={formData.preferred_size}
                    onValueChange={(value) => setFormData({ ...formData, preferred_size: value })}
                  >
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="small">Small</SelectItem>
                      <SelectItem value="medium">Medium</SelectItem>
                      <SelectItem value="large">Large</SelectItem>
                      <SelectItem value="extra_large">Extra Large</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <div className="space-y-2">
                  <Label htmlFor="alternate_size">Alternate Size</Label>
                  <Select
                    value={formData.alternate_size}
                    onValueChange={(value) => setFormData({ ...formData, alternate_size: value })}
                  >
                    <SelectTrigger>
                      <SelectValue placeholder="None" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="">None</SelectItem>
                      <SelectItem value="small">Small</SelectItem>
                      <SelectItem value="medium">Medium</SelectItem>
                      <SelectItem value="large">Large</SelectItem>
                      <SelectItem value="extra_large">Extra Large</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="preferred_location">Preferred Location</Label>
                  <Select
                    value={formData.preferred_location}
                    onValueChange={(value) => setFormData({ ...formData, preferred_location: value })}
                  >
                    <SelectTrigger>
                      <SelectValue placeholder="Any" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="">Any</SelectItem>
                      <SelectItem value="ground_floor">Ground Floor</SelectItem>
                      <SelectItem value="upper_floor">Upper Floor</SelectItem>
                      <SelectItem value="near_entrance">Near Entrance</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <div className="space-y-2">
                  <Label htmlFor="expected_usage_frequency">Expected Usage Frequency</Label>
                  <Select
                    value={formData.expected_usage_frequency}
                    onValueChange={(value) => setFormData({ ...formData, expected_usage_frequency: value })}
                  >
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="daily">Daily</SelectItem>
                      <SelectItem value="weekly">Weekly</SelectItem>
                      <SelectItem value="monthly">Monthly</SelectItem>
                      <SelectItem value="occasional">Occasional</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>

              <div className="space-y-2">
                <Label htmlFor="advance_rent_years">Advance Rent Payment (Years)</Label>
                <Input
                  id="advance_rent_years"
                  type="number"
                  min="0"
                  max="10"
                  value={formData.advance_rent_years}
                  onChange={(e) => setFormData({ ...formData, advance_rent_years: parseInt(e.target.value) })}
                  placeholder="0"
                />
                <p className="text-xs text-gray-500">Paying advance rent increases priority score</p>
              </div>
            </div>
          )}

          {/* Step 3: Joint Holders & Documents */}
          {currentStep === 3 && (
            <div className="space-y-4">
              <h3 className="text-lg font-medium">Joint Holders & Documents</h3>
              
              <div className="space-y-4">
                <h4 className="text-sm font-medium text-gray-700">Joint Holders (Optional)</h4>
                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="joint_holder_1_id">Joint Holder 1 ID</Label>
                    <Input
                      id="joint_holder_1_id"
                      value={formData.joint_holder_1_id}
                      onChange={(e) => setFormData({ ...formData, joint_holder_1_id: e.target.value })}
                      placeholder="Search customer..."
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="joint_holder_2_id">Joint Holder 2 ID</Label>
                    <Input
                      id="joint_holder_2_id"
                      value={formData.joint_holder_2_id}
                      onChange={(e) => setFormData({ ...formData, joint_holder_2_id: e.target.value })}
                      placeholder="Search customer..."
                    />
                  </div>
                </div>
              </div>

              <div className="space-y-4 border-t pt-4">
                <h4 className="text-sm font-medium text-gray-700">KYC & Document Upload</h4>
                
                <div className="flex items-center space-x-2">
                  <input
                    type="checkbox"
                    id="kyc_verified"
                    checked={formData.kyc_verified}
                    onChange={(e) => setFormData({ ...formData, kyc_verified: e.target.checked })}
                    className="rounded"
                  />
                  <Label htmlFor="kyc_verified">KYC Verified</Label>
                </div>

                <div className="space-y-2">
                  <Label>Upload Documents</Label>
                  <div className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center hover:border-blue-400 transition-colors cursor-pointer">
                    <Upload className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                    <p className="text-sm text-gray-600 mb-2">
                      Click to upload or drag and drop
                    </p>
                    <p className="text-xs text-gray-500">
                      ID Proof, Address Proof, Photo, Signature (PDF, JPG, PNG up to 10MB)
                    </p>
                    <Input
                      type="file"
                      multiple
                      accept=".pdf,.jpg,.jpeg,.png"
                      className="hidden"
                      id="document-upload"
                    />
                  </div>
                  {formData.documents && formData.documents.length > 0 && (
                    <div className="mt-2">
                      <p className="text-sm text-gray-700">{formData.documents.length} file(s) selected</p>
                    </div>
                  )}
                </div>
              </div>
            </div>
          )}

          {/* Step 4: Review & Submit */}
          {currentStep === 4 && (
            <div className="space-y-4">
              <h3 className="text-lg font-medium">Review & Submit</h3>
              
              <Card>
                <CardHeader>
                  <CardTitle className="text-base">Application Summary</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="grid grid-cols-2 gap-4 text-sm">
                    <div>
                      <p className="text-gray-500">Application Number</p>
                      <p className="font-medium">{formData.application_number || 'AUTO-GENERATED'}</p>
                    </div>
                    <div>
                      <p className="text-gray-500">Application Type</p>
                      <p className="font-medium">{formData.application_type}</p>
                    </div>
                    <div>
                      <p className="text-gray-500">Customer ID</p>
                      <p className="font-medium">{formData.customer_id}</p>
                    </div>
                    <div>
                      <p className="text-gray-500">Application Date</p>
                      <p className="font-medium">{formatDate(formData.application_date)}</p>
                    </div>
                    <div>
                      <p className="text-gray-500">Preferred Size</p>
                      <p className="font-medium">{formData.preferred_size}</p>
                    </div>
                    <div>
                      <p className="text-gray-500">Preferred Location</p>
                      <p className="font-medium">{formData.preferred_location || 'Any'}</p>
                    </div>
                    {formData.advance_rent_years > 0 && (
                      <div className="col-span-2">
                        <p className="text-gray-500">Advance Rent Payment</p>
                        <p className="font-medium">{formData.advance_rent_years} year(s)</p>
                      </div>
                    )}
                  </div>

                  {formData.purpose && (
                    <div className="border-t pt-4">
                      <p className="text-gray-500 text-sm mb-2">Purpose</p>
                      <p className="text-sm">{formData.purpose}</p>
                    </div>
                  )}
                </CardContent>
              </Card>

              <div className="space-y-2">
                <Label htmlFor="remarks">Additional Remarks</Label>
                <Textarea
                  id="remarks"
                  value={formData.remarks}
                  onChange={(e) => setFormData({ ...formData, remarks: e.target.value })}
                  placeholder="Any additional notes or special requests..."
                  rows={3}
                />
              </div>

              <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                <div className="flex items-start gap-3">
                  <AlertTriangle className="h-5 w-5 text-blue-600 mt-0.5" />
                  <div className="text-sm text-blue-900">
                    <p className="font-medium mb-1">Before Submitting</p>
                    <ul className="list-disc list-inside space-y-1 text-blue-800">
                      <li>Verify all customer information is correct</li>
                      <li>Ensure KYC documents are uploaded and verified</li>
                      <li>Check locker preferences and availability</li>
                      <li>Review financial terms and advance payment</li>
                    </ul>
                  </div>
                </div>
              </div>
            </div>
          )}

          <DialogFooter className="flex justify-between">
            <div>
              {currentStep > 1 && (
                <Button type="button" variant="outline" onClick={handlePrevious}>
                  Previous
                </Button>
              )}
            </div>
            <div className="flex gap-2">
              <Button type="button" variant="outline" onClick={() => onOpenChange(false)}>
                Cancel
              </Button>
              {currentStep < 4 ? (
                <Button type="button" onClick={handleNext}>
                  Next
                </Button>
              ) : (
                <Button type="submit" disabled={isLoading}>
                  {isLoading ? 'Submitting...' : 'Submit Application'}
                </Button>
              )}
            </div>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  )
}

// Application View Dialog Component
function ApplicationViewDialog({
  open,
  onOpenChange,
  application,
}: {
  open: boolean
  onOpenChange: (open: boolean) => void
  application: LockerApplication
}) {
  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-3xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>Application Details</DialogTitle>
          <DialogDescription>
            Application #{application.application_number}
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-6">
          {/* Status Banner */}
          <div className={`p-4 rounded-lg border-l-4 ${
            application.status === ApplicationStatus.APPROVED ? 'bg-green-50 border-green-500' :
            application.status === ApplicationStatus.REJECTED ? 'bg-red-50 border-red-500' :
            'bg-blue-50 border-blue-500'
          }`}>
            <div className="flex items-center justify-between">
              <div>
                <p className="font-medium">Status: {application.status.replace('_', ' ').toUpperCase()}</p>
                {application.current_stage && (
                  <p className="text-sm mt-1">Stage: {application.current_stage.replace('_', ' ')}</p>
                )}
              </div>
              <Badge className={
                application.status === ApplicationStatus.APPROVED ? 'bg-green-100 text-green-800' :
                application.status === ApplicationStatus.REJECTED ? 'bg-red-100 text-red-800' :
                'bg-blue-100 text-blue-800'
              }>
                Priority: {application.priority_score || 0}
              </Badge>
            </div>
          </div>

          {/* Basic Information */}
          <div className="space-y-3">
            <h3 className="font-medium text-gray-900">Basic Information</h3>
            <div className="grid grid-cols-2 gap-4 text-sm">
              <div>
                <p className="text-gray-500">Application Type</p>
                <p className="font-medium">{application.application_type}</p>
              </div>
              <div>
                <p className="text-gray-500">Application Date</p>
                <p className="font-medium">{formatDate(application.application_date)}</p>
              </div>
              <div>
                <p className="text-gray-500">Customer ID</p>
                <p className="font-medium">{application.customer_id}</p>
              </div>
              <div>
                <p className="text-gray-500">Branch</p>
                <p className="font-medium">{application.branch_id || 'N/A'}</p>
              </div>
            </div>
          </div>

          {/* Locker Preferences */}
          <div className="space-y-3 border-t pt-4">
            <h3 className="font-medium text-gray-900">Locker Preferences</h3>
            <div className="grid grid-cols-2 gap-4 text-sm">
              <div>
                <p className="text-gray-500">Preferred Size</p>
                <p className="font-medium">{application.preferred_size}</p>
              </div>
              <div>
                <p className="text-gray-500">Alternate Size</p>
                <p className="font-medium">{application.alternate_size || 'None'}</p>
              </div>
              <div>
                <p className="text-gray-500">Preferred Location</p>
                <p className="font-medium">{application.preferred_location || 'Any'}</p>
              </div>
              <div>
                <p className="text-gray-500">Usage Frequency</p>
                <p className="font-medium">{application.expected_usage_frequency || 'N/A'}</p>
              </div>
            </div>
          </div>

          {/* Purpose */}
          {application.purpose && (
            <div className="space-y-2 border-t pt-4">
              <h3 className="font-medium text-gray-900">Purpose</h3>
              <p className="text-sm text-gray-700">{application.purpose}</p>
            </div>
          )}

          {/* Priority Score Breakdown */}
          {application.priority_breakdown && (
            <div className="space-y-3 border-t pt-4">
              <h3 className="font-medium text-gray-900">Priority Score Breakdown</h3>
              <div className="bg-gray-50 rounded-lg p-4 space-y-2 text-sm">
                {Object.entries(application.priority_breakdown).map(([key, value]) => (
                  <div key={key} className="flex justify-between">
                    <span className="text-gray-600">{key.replace('_', ' ')}</span>
                    <span className="font-medium">{value} pts</span>
                  </div>
                ))}
                <div className="flex justify-between border-t pt-2 font-medium">
                  <span>Total Score</span>
                  <span>{application.priority_score}</span>
                </div>
              </div>
            </div>
          )}

          {/* Joint Holders */}
          {(application.joint_holder_1_id || application.joint_holder_2_id) && (
            <div className="space-y-2 border-t pt-4">
              <h3 className="font-medium text-gray-900">Joint Holders</h3>
              <div className="text-sm space-y-1">
                {application.joint_holder_1_id && (
                  <p>Joint Holder 1: {application.joint_holder_1_id}</p>
                )}
                {application.joint_holder_2_id && (
                  <p>Joint Holder 2: {application.joint_holder_2_id}</p>
                )}
              </div>
            </div>
          )}

          {/* Documents */}
          {application.documents && application.documents.length > 0 && (
            <div className="space-y-2 border-t pt-4">
              <h3 className="font-medium text-gray-900">Documents</h3>
              <div className="space-y-2">
                {application.documents.map((doc: any, index: number) => (
                  <div key={index} className="flex items-center justify-between p-2 bg-gray-50 rounded">
                    <div className="flex items-center gap-2">
                      <FileText className="h-4 w-4 text-gray-400" />
                      <span className="text-sm">{doc.name || `Document ${index + 1}`}</span>
                    </div>
                    <Button variant="ghost" size="sm">
                      <Eye className="h-4 w-4" />
                    </Button>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Remarks */}
          {application.remarks && (
            <div className="space-y-2 border-t pt-4">
              <h3 className="font-medium text-gray-900">Remarks</h3>
              <p className="text-sm text-gray-700">{application.remarks}</p>
            </div>
          )}
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
