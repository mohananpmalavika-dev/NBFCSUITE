'use client'

import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { 
  CheckCircle, XCircle, Eye, Clock, FileText, Shield, 
  User, DollarSign, AlertTriangle, TrendingUp, ClipboardCheck
} from 'lucide-react'
import { DashboardLayout } from '@/components/layout/dashboard-layout'
import { Button } from '@/components/ui/button'
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
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Textarea } from '@/components/ui/textarea'
import { Checkbox } from '@/components/ui/checkbox'
import { 
  applicationService, 
  ApplicationStatus, 
  ApplicationStage,
  type LockerApplication 
} from '@/services/locker.service'
import { formatCurrency, formatDate } from '@/lib/utils'
import { toast } from 'sonner'

export default function ApprovalsPage() {
  const [selectedStage, setSelectedStage] = useState<ApplicationStage>(ApplicationStage.DOCUMENT_VERIFICATION)
  const [isReviewOpen, setIsReviewOpen] = useState(false)
  const [isApproveOpen, setIsApproveOpen] = useState(false)
  const [isRejectOpen, setIsRejectOpen] = useState(false)
  const [selectedApplication, setSelectedApplication] = useState<LockerApplication | null>(null)

  const queryClient = useQueryClient()

  const { data: pendingData, isLoading } = useQuery({
    queryKey: ['pending-approvals'],
    queryFn: () => applicationService.getPendingApprovals(),
  })

  const { data: analyticsData } = useQuery({
    queryKey: ['applications-analytics'],
    queryFn: () => applicationService.getAnalytics(),
  })

  const reviewMutation = useMutation({
    mutationFn: ({ id, data }: { id: string; data: any }) =>
      applicationService.reviewApplication(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['pending-approvals'] })
      queryClient.invalidateQueries({ queryKey: ['applications-analytics'] })
      setIsReviewOpen(false)
      toast.success('Application reviewed successfully')
    },
    onError: () => {
      toast.error('Failed to review application')
    },
  })

  const approveMutation = useMutation({
    mutationFn: ({ id, data }: { id: string; data: any }) =>
      applicationService.approveApplication(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['pending-approvals'] })
      queryClient.invalidateQueries({ queryKey: ['applications-analytics'] })
      setIsApproveOpen(false)
      toast.success('Application approved successfully')
    },
    onError: () => {
      toast.error('Failed to approve application')
    },
  })

  const rejectMutation = useMutation({
    mutationFn: ({ id, reason }: { id: string; reason: string }) =>
      applicationService.approveApplication(id, { approved: false, remarks: reason }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['pending-approvals'] })
      queryClient.invalidateQueries({ queryKey: ['applications-analytics'] })
      setIsRejectOpen(false)
      toast.success('Application rejected')
    },
    onError: () => {
      toast.error('Failed to reject application')
    },
  })

  const getStageIcon = (stage: ApplicationStage) => {
    const icons = {
      document_verification: FileText,
      credit_check: DollarSign,
      manager_review: User,
      final_approval: CheckCircle,
    }
    return icons[stage] || FileText
  }

  const getStageColor = (stage: ApplicationStage) => {
    const colors = {
      document_verification: 'bg-blue-100 text-blue-700',
      credit_check: 'bg-purple-100 text-purple-700',
      manager_review: 'bg-orange-100 text-orange-700',
      final_approval: 'bg-green-100 text-green-700',
    }
    return colors[stage] || 'bg-gray-100 text-gray-700'
  }

  const handleReview = (application: LockerApplication) => {
    setSelectedApplication(application)
    setIsReviewOpen(true)
  }

  const handleApprove = (application: LockerApplication) => {
    setSelectedApplication(application)
    setIsApproveOpen(true)
  }

  const handleReject = (application: LockerApplication) => {
    setSelectedApplication(application)
    setIsRejectOpen(true)
  }

  // Filter applications by stage
  const applicationsByStage = pendingData?.data?.pending_approvals?.filter(
    (app: LockerApplication) => app.current_stage === selectedStage
  ) || []

  return (
    <DashboardLayout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Application Approvals</h1>
            <p className="text-gray-600 mt-1">Multi-stage approval workflow management</p>
          </div>
        </div>

        {/* Analytics Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <Card className="border-l-4 border-l-yellow-500">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Pending Approvals</CardTitle>
              <Clock className="h-4 w-4 text-yellow-600" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-yellow-600">
                {pendingData?.data?.pending_approvals?.length || 0}
              </div>
              <p className="text-xs text-gray-600 mt-1">Awaiting action</p>
            </CardContent>
          </Card>

          <Card className="border-l-4 border-l-green-500">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Approved Today</CardTitle>
              <CheckCircle className="h-4 w-4 text-green-600" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-green-600">
                {analyticsData?.data?.approved_today || 0}
              </div>
              <p className="text-xs text-gray-600 mt-1">This day</p>
            </CardContent>
          </Card>

          <Card className="border-l-4 border-l-red-500">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Rejected</CardTitle>
              <XCircle className="h-4 w-4 text-red-600" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-red-600">
                {analyticsData?.data?.rejected_applications || 0}
              </div>
              <p className="text-xs text-gray-600 mt-1">Total</p>
            </CardContent>
          </Card>

          <Card className="border-l-4 border-l-blue-500">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Approval Rate</CardTitle>
              <TrendingUp className="h-4 w-4 text-blue-600" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-blue-600">
                {analyticsData?.data?.approval_rate?.toFixed(0) || 0}%
              </div>
              <p className="text-xs text-gray-600 mt-1">Success rate</p>
            </CardContent>
          </Card>
        </div>

        {/* Approval Stages Tabs */}
        <Card>
          <CardHeader>
            <CardTitle>Approval Pipeline</CardTitle>
            <CardDescription>Review applications at each stage of the approval workflow</CardDescription>
          </CardHeader>
          <CardContent>
            <Tabs value={selectedStage} onValueChange={(value) => setSelectedStage(value as ApplicationStage)}>
              <TabsList className="grid w-full grid-cols-4">
                <TabsTrigger value={ApplicationStage.DOCUMENT_VERIFICATION} className="flex items-center gap-2">
                  <FileText className="h-4 w-4" />
                  <span className="hidden sm:inline">Documents</span>
                  {pendingData?.data?.pending_approvals?.filter(
                    (a: LockerApplication) => a.current_stage === ApplicationStage.DOCUMENT_VERIFICATION
                  ).length > 0 && (
                    <Badge variant="destructive" className="ml-2">
                      {pendingData.data.pending_approvals.filter(
                        (a: LockerApplication) => a.current_stage === ApplicationStage.DOCUMENT_VERIFICATION
                      ).length}
                    </Badge>
                  )}
                </TabsTrigger>
                <TabsTrigger value={ApplicationStage.CREDIT_CHECK} className="flex items-center gap-2">
                  <DollarSign className="h-4 w-4" />
                  <span className="hidden sm:inline">Credit</span>
                  {pendingData?.data?.pending_approvals?.filter(
                    (a: LockerApplication) => a.current_stage === ApplicationStage.CREDIT_CHECK
                  ).length > 0 && (
                    <Badge variant="destructive" className="ml-2">
                      {pendingData.data.pending_approvals.filter(
                        (a: LockerApplication) => a.current_stage === ApplicationStage.CREDIT_CHECK
                      ).length}
                    </Badge>
                  )}
                </TabsTrigger>
                <TabsTrigger value={ApplicationStage.MANAGER_REVIEW} className="flex items-center gap-2">
                  <User className="h-4 w-4" />
                  <span className="hidden sm:inline">Manager</span>
                  {pendingData?.data?.pending_approvals?.filter(
                    (a: LockerApplication) => a.current_stage === ApplicationStage.MANAGER_REVIEW
                  ).length > 0 && (
                    <Badge variant="destructive" className="ml-2">
                      {pendingData.data.pending_approvals.filter(
                        (a: LockerApplication) => a.current_stage === ApplicationStage.MANAGER_REVIEW
                      ).length}
                    </Badge>
                  )}
                </TabsTrigger>
                <TabsTrigger value={ApplicationStage.FINAL_APPROVAL} className="flex items-center gap-2">
                  <CheckCircle className="h-4 w-4" />
                  <span className="hidden sm:inline">Final</span>
                  {pendingData?.data?.pending_approvals?.filter(
                    (a: LockerApplication) => a.current_stage === ApplicationStage.FINAL_APPROVAL
                  ).length > 0 && (
                    <Badge variant="destructive" className="ml-2">
                      {pendingData.data.pending_approvals.filter(
                        (a: LockerApplication) => a.current_stage === ApplicationStage.FINAL_APPROVAL
                      ).length}
                    </Badge>
                  )}
                </TabsTrigger>
              </TabsList>

              {/* Stage Content */}
              <TabsContent value={selectedStage} className="mt-6">
                <div className="space-y-4">
                  {isLoading ? (
                    [...Array(3)].map((_, i) => (
                      <Card key={i}>
                        <CardContent className="p-6">
                          <div className="space-y-3">
                            <Skeleton className="h-6 w-48" />
                            <Skeleton className="h-4 w-full" />
                            <Skeleton className="h-4 w-3/4" />
                          </div>
                        </CardContent>
                      </Card>
                    ))
                  ) : applicationsByStage.length > 0 ? (
                    applicationsByStage.map((application: LockerApplication) => (
                      <Card key={application.id} className="hover:shadow-md transition-shadow">
                        <CardContent className="p-6">
                          <div className="flex items-start justify-between">
                            <div className="flex-1 space-y-3">
                              {/* Header */}
                              <div className="flex items-center justify-between">
                                <div className="flex items-center gap-3">
                                  <div className={`p-2 rounded-lg ${getStageColor(selectedStage)}`}>
                                    {(() => {
                                      const Icon = getStageIcon(selectedStage)
                                      return <Icon className="h-5 w-5" />
                                    })()}
                                  </div>
                                  <div>
                                    <h3 className="text-lg font-semibold text-gray-900">
                                      {application.application_number}
                                    </h3>
                                    <p className="text-sm text-gray-500">
                                      {formatDate(application.application_date)}
                                    </p>
                                  </div>
                                </div>
                                <Badge className={getStageColor(selectedStage)}>
                                  {selectedStage.replace('_', ' ').toUpperCase()}
                                </Badge>
                              </div>

                              {/* Application Details */}
                              <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                                <div>
                                  <p className="text-gray-500">Customer ID</p>
                                  <p className="font-medium">{application.customer_id}</p>
                                </div>
                                <div>
                                  <p className="text-gray-500">Preferred Size</p>
                                  <p className="font-medium">{application.preferred_size}</p>
                                </div>
                                <div>
                                  <p className="text-gray-500">Priority Score</p>
                                  <p className="font-medium">{application.priority_score || 0}</p>
                                </div>
                                <div>
                                  <p className="text-gray-500">Application Type</p>
                                  <p className="font-medium">{application.application_type}</p>
                                </div>
                              </div>

                              {/* Stage-Specific Checklist */}
                              {selectedStage === ApplicationStage.DOCUMENT_VERIFICATION && (
                                <div className="bg-blue-50 rounded-lg p-4 mt-4">
                                  <h4 className="text-sm font-medium text-blue-900 mb-3">Document Verification Checklist</h4>
                                  <div className="space-y-2 text-sm">
                                    <div className="flex items-center gap-2">
                                      <Checkbox id={`kyc-${application.id}`} checked={application.kyc_verified} />
                                      <label htmlFor={`kyc-${application.id}`}>KYC Documents Verified</label>
                                    </div>
                                    <div className="flex items-center gap-2">
                                      <Checkbox id={`id-${application.id}`} />
                                      <label htmlFor={`id-${application.id}`}>ID Proof Validated</label>
                                    </div>
                                    <div className="flex items-center gap-2">
                                      <Checkbox id={`address-${application.id}`} />
                                      <label htmlFor={`address-${application.id}`}>Address Proof Validated</label>
                                    </div>
                                    <div className="flex items-center gap-2">
                                      <Checkbox id={`signature-${application.id}`} />
                                      <label htmlFor={`signature-${application.id}`}>Signature Verified</label>
                                    </div>
                                  </div>
                                </div>
                              )}

                              {selectedStage === ApplicationStage.CREDIT_CHECK && (
                                <div className="bg-purple-50 rounded-lg p-4 mt-4">
                                  <h4 className="text-sm font-medium text-purple-900 mb-3">Credit Assessment Checklist</h4>
                                  <div className="space-y-2 text-sm">
                                    <div className="flex items-center gap-2">
                                      <Checkbox id={`credit-score-${application.id}`} />
                                      <label htmlFor={`credit-score-${application.id}`}>Credit Score Checked</label>
                                    </div>
                                    <div className="flex items-center gap-2">
                                      <Checkbox id={`existing-${application.id}`} />
                                      <label htmlFor={`existing-${application.id}`}>Existing Customer Records Reviewed</label>
                                    </div>
                                    <div className="flex items-center gap-2">
                                      <Checkbox id={`deposits-${application.id}`} />
                                      <label htmlFor={`deposits-${application.id}`}>Deposit Relationships Verified</label>
                                    </div>
                                    <div className="flex items-center gap-2">
                                      <Checkbox id={`loans-${application.id}`} />
                                      <label htmlFor={`loans-${application.id}`}>Loan History Checked</label>
                                    </div>
                                  </div>
                                </div>
                              )}

                              {selectedStage === ApplicationStage.MANAGER_REVIEW && (
                                <div className="bg-orange-50 rounded-lg p-4 mt-4">
                                  <h4 className="text-sm font-medium text-orange-900 mb-3">Manager Review Points</h4>
                                  <div className="space-y-2 text-sm">
                                    <div className="flex items-center gap-2">
                                      <Checkbox id={`purpose-${application.id}`} />
                                      <label htmlFor={`purpose-${application.id}`}>Purpose Reviewed</label>
                                    </div>
                                    <div className="flex items-center gap-2">
                                      <Checkbox id={`priority-${application.id}`} />
                                      <label htmlFor={`priority-${application.id}`}>Priority Score Validated</label>
                                    </div>
                                    <div className="flex items-center gap-2">
                                      <Checkbox id={`availability-${application.id}`} />
                                      <label htmlFor={`availability-${application.id}`}>Locker Availability Confirmed</label>
                                    </div>
                                    <div className="flex items-center gap-2">
                                      <Checkbox id={`risk-${application.id}`} />
                                      <label htmlFor={`risk-${application.id}`}>Risk Assessment Complete</label>
                                    </div>
                                  </div>
                                </div>
                              )}

                              {selectedStage === ApplicationStage.FINAL_APPROVAL && (
                                <div className="bg-green-50 rounded-lg p-4 mt-4">
                                  <h4 className="text-sm font-medium text-green-900 mb-3">Final Approval Checklist</h4>
                                  <div className="space-y-2 text-sm">
                                    <div className="flex items-center gap-2">
                                      <Checkbox id={`all-docs-${application.id}`} />
                                      <label htmlFor={`all-docs-${application.id}`}>All Documentation Complete</label>
                                    </div>
                                    <div className="flex items-center gap-2">
                                      <Checkbox id={`credit-clear-${application.id}`} />
                                      <label htmlFor={`credit-clear-${application.id}`}>Credit Check Passed</label>
                                    </div>
                                    <div className="flex items-center gap-2">
                                      <Checkbox id={`manager-approved-${application.id}`} />
                                      <label htmlFor={`manager-approved-${application.id}`}>Manager Approval Received</label>
                                    </div>
                                    <div className="flex items-center gap-2">
                                      <Checkbox id={`terms-${application.id}`} />
                                      <label htmlFor={`terms-${application.id}`}>Terms & Conditions Accepted</label>
                                    </div>
                                  </div>
                                </div>
                              )}

                              {/* Purpose */}
                              {application.purpose && (
                                <div className="border-t pt-3">
                                  <p className="text-sm text-gray-600 mb-1">Purpose:</p>
                                  <p className="text-sm text-gray-900">{application.purpose}</p>
                                </div>
                              )}
                            </div>

                            {/* Action Buttons */}
                            <div className="flex flex-col gap-2 ml-4">
                              <Button
                                variant="outline"
                                size="sm"
                                onClick={() => handleReview(application)}
                              >
                                <Eye className="h-4 w-4 mr-2" />
                                Review
                              </Button>
                              <Button
                                variant="default"
                                size="sm"
                                className="bg-green-600 hover:bg-green-700"
                                onClick={() => handleApprove(application)}
                              >
                                <CheckCircle className="h-4 w-4 mr-2" />
                                Approve
                              </Button>
                              <Button
                                variant="outline"
                                size="sm"
                                className="text-red-600 border-red-600 hover:bg-red-50"
                                onClick={() => handleReject(application)}
                              >
                                <XCircle className="h-4 w-4 mr-2" />
                                Reject
                              </Button>
                            </div>
                          </div>
                        </CardContent>
                      </Card>
                    ))
                  ) : (
                    <Card>
                      <CardContent className="p-12 text-center">
                        <ClipboardCheck className="h-16 w-16 text-gray-300 mx-auto mb-4" />
                        <h3 className="text-lg font-medium text-gray-900 mb-2">No Pending Applications</h3>
                        <p className="text-gray-500">
                          There are no applications waiting for review at this stage.
                        </p>
                      </CardContent>
                    </Card>
                  )}
                </div>
              </TabsContent>
            </Tabs>
          </CardContent>
        </Card>

        {/* Dialogs */}
        {selectedApplication && (
          <>
            <ReviewDialog
              open={isReviewOpen}
              onOpenChange={setIsReviewOpen}
              application={selectedApplication}
              onSubmit={(data) => reviewMutation.mutate({ id: selectedApplication.id, data })}
              isLoading={reviewMutation.isPending}
            />
            <ApproveDialog
              open={isApproveOpen}
              onOpenChange={setIsApproveOpen}
              application={selectedApplication}
              onSubmit={(data) => approveMutation.mutate({ id: selectedApplication.id, data })}
              isLoading={approveMutation.isPending}
            />
            <RejectDialog
              open={isRejectOpen}
              onOpenChange={setIsRejectOpen}
              application={selectedApplication}
              onSubmit={(reason) => rejectMutation.mutate({ id: selectedApplication.id, reason })}
              isLoading={rejectMutation.isPending}
            />
          </>
        )}
      </div>
    </DashboardLayout>
  )
}

// Review Dialog Component
function ReviewDialog({
  open,
  onOpenChange,
  application,
  onSubmit,
  isLoading,
}: {
  open: boolean
  onOpenChange: (open: boolean) => void
  application: LockerApplication
  onSubmit: (data: any) => void
  isLoading: boolean
}) {
  const [remarks, setRemarks] = useState('')

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    onSubmit({ remarks })
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-3xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>Review Application</DialogTitle>
          <DialogDescription>
            Application #{application.application_number}
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-6">
          {/* Application Summary */}
          <Card className="bg-gradient-to-r from-blue-50 to-purple-50">
            <CardContent className="pt-6">
              <div className="grid grid-cols-2 md:grid-cols-3 gap-4 text-sm">
                <div>
                  <p className="text-gray-600">Application Number</p>
                  <p className="font-medium">{application.application_number}</p>
                </div>
                <div>
                  <p className="text-gray-600">Customer ID</p>
                  <p className="font-medium">{application.customer_id}</p>
                </div>
                <div>
                  <p className="text-gray-600">Application Date</p>
                  <p className="font-medium">{formatDate(application.application_date)}</p>
                </div>
                <div>
                  <p className="text-gray-600">Type</p>
                  <p className="font-medium">{application.application_type}</p>
                </div>
                <div>
                  <p className="text-gray-600">Preferred Size</p>
                  <p className="font-medium">{application.preferred_size}</p>
                </div>
                <div>
                  <p className="text-gray-600">Priority Score</p>
                  <p className="font-medium">{application.priority_score || 0}</p>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Current Stage */}
          <div>
            <h3 className="text-sm font-medium text-gray-900 mb-3">Current Stage</h3>
            <Badge className="text-base px-4 py-2">
              {application.current_stage?.replace('_', ' ').toUpperCase() || 'N/A'}
            </Badge>
          </div>

          {/* Purpose */}
          {application.purpose && (
            <div>
              <h3 className="text-sm font-medium text-gray-900 mb-2">Purpose</h3>
              <p className="text-sm text-gray-700 bg-gray-50 rounded-lg p-3">
                {application.purpose}
              </p>
            </div>
          )}

          {/* Priority Breakdown */}
          {application.priority_breakdown && (
            <div>
              <h3 className="text-sm font-medium text-gray-900 mb-3">Priority Score Breakdown</h3>
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

          {/* Documents */}
          {application.documents && application.documents.length > 0 && (
            <div>
              <h3 className="text-sm font-medium text-gray-900 mb-3">Documents</h3>
              <div className="space-y-2">
                {application.documents.map((doc: any, index: number) => (
                  <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                    <div className="flex items-center gap-3">
                      <FileText className="h-5 w-5 text-gray-400" />
                      <span className="text-sm font-medium">{doc.name || `Document ${index + 1}`}</span>
                    </div>
                    <Button variant="ghost" size="sm">
                      <Eye className="h-4 w-4" />
                    </Button>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Review Form */}
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="remarks">Review Remarks</Label>
              <Textarea
                id="remarks"
                value={remarks}
                onChange={(e) => setRemarks(e.target.value)}
                placeholder="Add your review comments..."
                rows={4}
              />
            </div>

            <DialogFooter>
              <Button type="button" variant="outline" onClick={() => onOpenChange(false)}>
                Cancel
              </Button>
              <Button type="submit" disabled={isLoading}>
                {isLoading ? 'Submitting...' : 'Submit Review'}
              </Button>
            </DialogFooter>
          </form>
        </div>
      </DialogContent>
    </Dialog>
  )
}

// Approve Dialog Component
function ApproveDialog({
  open,
  onOpenChange,
  application,
  onSubmit,
  isLoading,
}: {
  open: boolean
  onOpenChange: (open: boolean) => void
  application: LockerApplication
  onSubmit: (data: any) => void
  isLoading: boolean
}) {
  const [formData, setFormData] = useState({
    approved: true,
    remarks: '',
    allocated_locker_id: '',
  })

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    onSubmit(formData)
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-2xl">
        <DialogHeader>
          <DialogTitle>Approve Application</DialogTitle>
          <DialogDescription>
            Approve application #{application.application_number}
          </DialogDescription>
        </DialogHeader>

        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Application Summary */}
          <Card className="bg-green-50 border-green-200">
            <CardContent className="pt-6">
              <div className="grid grid-cols-2 gap-4 text-sm">
                <div>
                  <p className="text-gray-600">Customer ID</p>
                  <p className="font-medium">{application.customer_id}</p>
                </div>
                <div>
                  <p className="text-gray-600">Application Type</p>
                  <p className="font-medium">{application.application_type}</p>
                </div>
                <div>
                  <p className="text-gray-600">Preferred Size</p>
                  <p className="font-medium">{application.preferred_size}</p>
                </div>
                <div>
                  <p className="text-gray-600">Priority Score</p>
                  <p className="font-medium">{application.priority_score || 0}</p>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Approval Details */}
          <div className="space-y-4">
            <h3 className="text-sm font-medium">Approval Details</h3>
            
            {application.current_stage === ApplicationStage.FINAL_APPROVAL && (
              <div className="space-y-2">
                <Label htmlFor="allocated_locker_id">Allocate Locker (Optional)</Label>
                <Input
                  id="allocated_locker_id"
                  value={formData.allocated_locker_id}
                  onChange={(e) => setFormData({ ...formData, allocated_locker_id: e.target.value })}
                  placeholder="Search and select locker..."
                />
                <p className="text-xs text-gray-500">
                  Leave blank to approve without immediate allocation
                </p>
              </div>
            )}

            <div className="space-y-2">
              <Label htmlFor="remarks">Approval Remarks</Label>
              <Textarea
                id="remarks"
                value={formData.remarks}
                onChange={(e) => setFormData({ ...formData, remarks: e.target.value })}
                placeholder="Add approval notes..."
                rows={3}
              />
            </div>
          </div>

          {/* Warning Notice */}
          <div className="bg-green-50 border border-green-200 rounded-lg p-4">
            <div className="flex items-start gap-3">
              <CheckCircle className="h-5 w-5 text-green-600 mt-0.5" />
              <div className="text-sm text-green-900">
                <p className="font-medium mb-1">Approval Confirmation</p>
                <ul className="list-disc list-inside space-y-1 text-green-800">
                  <li>Customer will be notified via email and SMS</li>
                  <li>Application moves to next stage or completion</li>
                  {application.current_stage === ApplicationStage.FINAL_APPROVAL && (
                    <li>If locker allocated, agreement creation will be initiated</li>
                  )}
                  <li>This action cannot be undone</li>
                </ul>
              </div>
            </div>
          </div>

          <DialogFooter>
            <Button type="button" variant="outline" onClick={() => onOpenChange(false)}>
              Cancel
            </Button>
            <Button 
              type="submit" 
              disabled={isLoading}
              className="bg-green-600 hover:bg-green-700"
            >
              {isLoading ? 'Approving...' : 'Approve Application'}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  )
}

// Reject Dialog Component
function RejectDialog({
  open,
  onOpenChange,
  application,
  onSubmit,
  isLoading,
}: {
  open: boolean
  onOpenChange: (open: boolean) => void
  application: LockerApplication
  onSubmit: (reason: string) => void
  isLoading: boolean
}) {
  const [reason, setReason] = useState('')

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (!reason.trim()) {
      toast.error('Please provide a rejection reason')
      return
    }
    onSubmit(reason)
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-2xl">
        <DialogHeader>
          <DialogTitle>Reject Application</DialogTitle>
          <DialogDescription>
            Reject application #{application.application_number}
          </DialogDescription>
        </DialogHeader>

        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Application Summary */}
          <Card className="bg-red-50 border-red-200">
            <CardContent className="pt-6">
              <div className="grid grid-cols-2 gap-4 text-sm">
                <div>
                  <p className="text-gray-600">Customer ID</p>
                  <p className="font-medium">{application.customer_id}</p>
                </div>
                <div>
                  <p className="text-gray-600">Application Number</p>
                  <p className="font-medium">{application.application_number}</p>
                </div>
                <div>
                  <p className="text-gray-600">Current Stage</p>
                  <p className="font-medium">{application.current_stage?.replace('_', ' ')}</p>
                </div>
                <div>
                  <p className="text-gray-600">Priority Score</p>
                  <p className="font-medium">{application.priority_score || 0}</p>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Rejection Reason */}
          <div className="space-y-2">
            <Label htmlFor="reason">Rejection Reason *</Label>
            <Textarea
              id="reason"
              value={reason}
              onChange={(e) => setReason(e.target.value)}
              placeholder="Please provide a clear reason for rejection..."
              rows={5}
              required
            />
            <p className="text-xs text-gray-500">
              This reason will be communicated to the customer
            </p>
          </div>

          {/* Warning Notice */}
          <div className="bg-red-50 border border-red-200 rounded-lg p-4">
            <div className="flex items-start gap-3">
              <AlertTriangle className="h-5 w-5 text-red-600 mt-0.5" />
              <div className="text-sm text-red-900">
                <p className="font-medium mb-1">Rejection Consequences</p>
                <ul className="list-disc list-inside space-y-1 text-red-800">
                  <li>Application status will be changed to REJECTED</li>
                  <li>Customer will be notified with the rejection reason</li>
                  <li>Customer may reapply after addressing the concerns</li>
                  <li>This action cannot be undone</li>
                </ul>
              </div>
            </div>
          </div>

          <DialogFooter>
            <Button type="button" variant="outline" onClick={() => onOpenChange(false)}>
              Cancel
            </Button>
            <Button 
              type="submit" 
              disabled={isLoading}
              className="bg-red-600 hover:bg-red-700"
            >
              {isLoading ? 'Rejecting...' : 'Reject Application'}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  )
}
