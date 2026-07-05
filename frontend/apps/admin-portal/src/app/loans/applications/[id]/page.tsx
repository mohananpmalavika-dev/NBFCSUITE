'use client'

import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useParams, useRouter } from 'next/navigation'
import Link from 'next/link'
import { 
  ArrowLeft, 
  CheckCircle,
  XCircle,
  Send,
  Calendar,
  User,
  Wallet,
  FileText,
  TrendingUp
} from 'lucide-react'
import { DashboardLayout } from '@/components/layout/dashboard-layout'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Skeleton } from '@/components/ui/skeleton'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Label } from '@/components/ui/label'
import { Input } from '@/components/ui/input'
import { useToast } from '@/hooks/use-toast'
import { loanService } from '@/services/loan.service'
import { formatCurrency, formatDate, getStatusColor, calculateEMI } from '@/lib/utils'

export default function LoanApplicationDetailPage() {
  const params = useParams()
  const router = useRouter()
  const { toast } = useToast()
  const queryClient = useQueryClient()
  const applicationId = params.id as string
  const [remarks, setRemarks] = useState('')

  const { data: application, isLoading } = useQuery({
    queryKey: ['loan-application', applicationId],
    queryFn: () => loanService.getApplication(applicationId),
  })

  const approveMutation = useMutation({
    mutationFn: () => loanService.approveApplication(applicationId, remarks),
    onSuccess: () => {
      toast({
        title: 'Success',
        description: 'Application approved successfully',
      })
      queryClient.invalidateQueries({ queryKey: ['loan-application', applicationId] })
      setRemarks('')
    },
    onError: (error: any) => {
      toast({
        title: 'Error',
        description: error.message || 'Failed to approve application',
        variant: 'destructive',
      })
    },
  })

  const rejectMutation = useMutation({
    mutationFn: () => loanService.rejectApplication(applicationId, remarks),
    onSuccess: () => {
      toast({
        title: 'Success',
        description: 'Application rejected',
      })
      queryClient.invalidateQueries({ queryKey: ['loan-application', applicationId] })
      setRemarks('')
    },
    onError: (error: any) => {
      toast({
        title: 'Error',
        description: error.message || 'Failed to reject application',
        variant: 'destructive',
      })
    },
  })

  const submitMutation = useMutation({
    mutationFn: () => loanService.submitApplication(applicationId),
    onSuccess: () => {
      toast({
        title: 'Success',
        description: 'Application submitted for review',
      })
      queryClient.invalidateQueries({ queryKey: ['loan-application', applicationId] })
    },
    onError: (error: any) => {
      toast({
        title: 'Error',
        description: error.message || 'Failed to submit application',
        variant: 'destructive',
      })
    },
  })

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

  if (!application?.data) {
    return (
      <DashboardLayout>
        <div className="text-center py-12">
          <p className="text-gray-600">Application not found</p>
        </div>
      </DashboardLayout>
    )
  }

  const app = application.data
  const canApprove = app.application_status === 'Submitted' || app.application_status === 'Under Review'
  const canSubmit = app.application_status === 'Draft'

  return (
    <DashboardLayout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <Link href="/loans/applications">
              <Button variant="ghost" size="icon">
                <ArrowLeft className="h-5 w-5" />
              </Button>
            </Link>
            <div>
              <h1 className="text-3xl font-bold text-gray-900">
                {app.application_number}
              </h1>
              <p className="text-gray-600 mt-1">
                Customer: {app.customer_name || 'N/A'}
              </p>
            </div>
          </div>
          <Badge className={getStatusColor(app.application_status)} style={{ fontSize: '1rem', padding: '0.5rem 1rem' }}>
            {app.application_status}
          </Badge>
        </div>

        {/* Action Buttons */}
        {(canSubmit || canApprove) && (
          <Card className="bg-blue-50 border-blue-200">
            <CardContent className="pt-6">
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="font-semibold text-gray-900 mb-1">
                    {canSubmit ? 'Submit Application' : 'Review Application'}
                  </h3>
                  <p className="text-sm text-gray-600">
                    {canSubmit 
                      ? 'Submit this application for review and approval'
                      : 'Review and approve or reject this loan application'}
                  </p>
                </div>
                <div className="flex gap-2">
                  {canSubmit && (
                    <Button
                      onClick={() => submitMutation.mutate()}
                      disabled={submitMutation.isPending}
                    >
                      <Send className="h-4 w-4 mr-2" />
                      Submit for Review
                    </Button>
                  )}
                  {canApprove && (
                    <>
                      <Button
                        variant="outline"
                        className="text-red-600 border-red-300 hover:bg-red-50"
                        onClick={() => {
                          if (!remarks) {
                            toast({
                              title: 'Remarks Required',
                              description: 'Please provide rejection remarks',
                              variant: 'destructive',
                            })
                            return
                          }
                          rejectMutation.mutate()
                        }}
                        disabled={rejectMutation.isPending}
                      >
                        <XCircle className="h-4 w-4 mr-2" />
                        Reject
                      </Button>
                      <Button
                        onClick={() => approveMutation.mutate()}
                        disabled={approveMutation.isPending}
                      >
                        <CheckCircle className="h-4 w-4 mr-2" />
                        Approve
                      </Button>
                    </>
                  )}
                </div>
              </div>
              {canApprove && (
                <div className="mt-4">
                  <Label htmlFor="remarks">Remarks</Label>
                  <Input
                    id="remarks"
                    placeholder="Enter approval/rejection remarks..."
                    value={remarks}
                    onChange={(e) => setRemarks(e.target.value)}
                    className="mt-2"
                  />
                </div>
              )}
            </CardContent>
          </Card>
        )}

        {/* Summary Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <SummaryCard
            label="Loan Amount"
            value={formatCurrency(app.loan_amount)}
            icon={Wallet}
          />
          <SummaryCard
            label="Tenure"
            value={`${app.tenure_months} months`}
            icon={Calendar}
          />
          <SummaryCard
            label="Interest Rate"
            value={`${app.interest_rate}% p.a.`}
            icon={TrendingUp}
          />
          <SummaryCard
            label="EMI Amount"
            value={formatCurrency(app.emi_amount)}
            icon={Wallet}
          />
        </div>

        {/* Tabs */}
        <Tabs defaultValue="details" className="space-y-6">
          <TabsList>
            <TabsTrigger value="details">Application Details</TabsTrigger>
            <TabsTrigger value="customer">Customer Info</TabsTrigger>
            <TabsTrigger value="documents">Documents</TabsTrigger>
            <TabsTrigger value="timeline">Timeline</TabsTrigger>
          </TabsList>

          {/* Application Details */}
          <TabsContent value="details" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle>Loan Details</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <InfoItem label="Application Number" value={app.application_number} />
                  <InfoItem label="Product" value={app.product_name || 'N/A'} />
                  <InfoItem label="Loan Amount" value={formatCurrency(app.loan_amount)} />
                  <InfoItem label="Tenure" value={`${app.tenure_months} months`} />
                  <InfoItem label="Interest Rate" value={`${app.interest_rate}% per annum`} />
                  <InfoItem label="EMI Amount" value={formatCurrency(app.emi_amount)} />
                  <InfoItem label="Total Payable" value={formatCurrency(app.emi_amount * app.tenure_months)} />
                  <InfoItem label="Total Interest" value={formatCurrency((app.emi_amount * app.tenure_months) - app.loan_amount)} />
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Purpose & Additional Info</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div>
                    <Label className="text-gray-600">Loan Purpose</Label>
                    <p className="mt-1 text-gray-900">{app.purpose || 'Not specified'}</p>
                  </div>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <InfoItem label="Applied On" value={formatDate(app.created_at)} />
                    <InfoItem label="Last Updated" value={formatDate(app.updated_at)} />
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Customer Info */}
          <TabsContent value="customer">
            <Card>
              <CardHeader>
                <CardTitle>Customer Information</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="flex items-start gap-3">
                  <User className="h-5 w-5 text-gray-400 mt-1" />
                  <div>
                    <p className="text-gray-900">{app.customer_name || 'Customer details not available'}</p>
                    <p className="text-sm text-gray-500 mt-1">
                      Customer ID: {app.customer_id}
                    </p>
                    <Link href={`/customers/${app.customer_id}`}>
                      <Button variant="link" className="px-0 h-auto mt-2">
                        View Full Customer Profile →
                      </Button>
                    </Link>
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Documents */}
          <TabsContent value="documents">
            <Card>
              <CardHeader>
                <CardTitle>Submitted Documents</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-center py-8 text-gray-500">
                  <FileText className="h-12 w-12 mx-auto text-gray-400 mb-2" />
                  <p>No documents uploaded yet</p>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Timeline */}
          <TabsContent value="timeline">
            <Card>
              <CardHeader>
                <CardTitle>Application Timeline</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <TimelineItem
                    status="completed"
                    title="Application Created"
                    date={formatDate(app.created_at)}
                    description="Application was created in the system"
                  />
                  {app.application_status !== 'Draft' && (
                    <TimelineItem
                      status="completed"
                      title="Application Submitted"
                      date={formatDate(app.updated_at)}
                      description="Application submitted for review"
                    />
                  )}
                  {(app.application_status === 'Approved' || app.application_status === 'Rejected') && (
                    <TimelineItem
                      status={app.application_status === 'Approved' ? 'completed' : 'failed'}
                      title={app.application_status}
                      date={formatDate(app.updated_at)}
                      description={`Application was ${app.application_status.toLowerCase()}`}
                    />
                  )}
                </div>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>
    </DashboardLayout>
  )
}

function SummaryCard({ label, value, icon: Icon }: { label: string; value: string; icon: any }) {
  return (
    <Card>
      <CardContent className="pt-6">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-sm text-gray-600 mb-1">{label}</p>
            <p className="text-xl font-bold text-gray-900">{value}</p>
          </div>
          <Icon className="h-8 w-8 text-gray-400" />
        </div>
      </CardContent>
    </Card>
  )
}

function InfoItem({ label, value }: { label: string; value: string }) {
  return (
    <div>
      <p className="text-sm text-gray-600 mb-1">{label}</p>
      <p className="text-gray-900 font-medium">{value}</p>
    </div>
  )
}

function TimelineItem({ 
  status, 
  title, 
  date, 
  description 
}: { 
  status: 'completed' | 'failed' | 'pending'
  title: string
  date: string
  description: string 
}) {
  const colors = {
    completed: 'bg-green-100 text-green-600',
    failed: 'bg-red-100 text-red-600',
    pending: 'bg-gray-100 text-gray-600',
  }

  const icons = {
    completed: CheckCircle,
    failed: XCircle,
    pending: Calendar,
  }

  const Icon = icons[status]

  return (
    <div className="flex items-start gap-4">
      <div className={`h-10 w-10 rounded-full ${colors[status]} flex items-center justify-center shrink-0`}>
        <Icon className="h-5 w-5" />
      </div>
      <div className="flex-1 min-w-0">
        <p className="font-medium text-gray-900">{title}</p>
        <p className="text-sm text-gray-600 mt-1">{description}</p>
        <p className="text-xs text-gray-500 mt-1">{date}</p>
      </div>
    </div>
  )
}
