'use client'

/**
 * NBS-7 Return Details Page
 * View and edit individual NBS-7 return with complete financial data
 */

import { use, useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Textarea } from '@/components/ui/textarea'
import {
  ArrowLeft,
  Save,
  CheckCircle,
  Send,
  Download,
  FileText,
  TrendingUp,
  AlertCircle,
} from 'lucide-react'
import { rbiReturnsService } from '@/services/rbi-returns.service'
import { formatCurrency, formatDate } from '@/lib/utils'
import { toast } from '@/components/ui/use-toast'
import { Skeleton } from '@/components/ui/skeleton'
import Link from 'next/link'
import { useRouter } from 'next/navigation'

export default function NBS7ReturnDetailsPage({
  params,
}: {
  params: Promise<{ id: string }>
}) {
  const { id } = use(params)
  const router = useRouter()
  const queryClient = useQueryClient()
  const [activeTab, setActiveTab] = useState('overview')
  const [isEditing, setIsEditing] = useState(false)

  // Form state for editing
  const [remarks, setRemarks] = useState('')

  // Fetch return details
  const { data: returnData, isLoading } = useQuery({
    queryKey: ['nbs7-return', id],
    queryFn: () => rbiReturnsService.getNBS7Return(id),
  })

  // Update mutation
  const updateMutation = useMutation({
    mutationFn: (data: any) => rbiReturnsService.updateNBS7Return(id, data),
    onSuccess: () => {
      toast({
        title: 'Return Updated',
        description: 'NBS-7 return has been updated successfully',
      })
      setIsEditing(false)
      queryClient.invalidateQueries({ queryKey: ['nbs7-return', id] })
    },
  })

  // Approve mutation
  const approveMutation = useMutation({
    mutationFn: () => rbiReturnsService.approveNBS7Return(id),
    onSuccess: () => {
      toast({
        title: 'Return Approved',
        description: 'NBS-7 return has been approved',
      })
      queryClient.invalidateQueries({ queryKey: ['nbs7-return', id] })
    },
  })

  // Submit mutation
  const submitMutation = useMutation({
    mutationFn: (reference: string) => rbiReturnsService.submitNBS7Return(id, reference),
    onSuccess: () => {
      toast({
        title: 'Return Submitted',
        description: 'NBS-7 return has been submitted to RBI',
      })
      queryClient.invalidateQueries({ queryKey: ['nbs7-return', id] })
    },
  })

  const handleSave = () => {
    updateMutation.mutate({ remarks })
  }

  const handleApprove = () => {
    if (confirm('Are you sure you want to approve this return?')) {
      approveMutation.mutate()
    }
  }

  const handleSubmit = () => {
    const reference = prompt('Enter RBI submission reference number:')
    if (reference) {
      submitMutation.mutate(reference)
    }
  }

  if (isLoading) {
    return <PageSkeleton />
  }

  if (!returnData) {
    return (
      <div className="text-center py-12">
        <p className="text-muted-foreground">Return not found</p>
        <Link href="/rbi-returns/nbs7">
          <Button className="mt-4">Back to Returns</Button>
        </Link>
      </div>
    )
  }

  const getStatusBadge = (status: string) => {
    const colors: Record<string, string> = {
      draft: 'bg-gray-100 text-gray-800',
      pending_review: 'bg-blue-100 text-blue-800',
      approved: 'bg-green-100 text-green-800',
      submitted: 'bg-purple-100 text-purple-800',
    }

    return (
      <Badge className={colors[status] || 'bg-gray-100'}>
        {status.replace('_', ' ').toUpperCase()}
      </Badge>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <Link href="/rbi-returns/nbs7">
            <Button variant="ghost" size="sm">
              <ArrowLeft className="h-4 w-4 mr-2" />
              Back
            </Button>
          </Link>
          <div>
            <h1 className="text-3xl font-bold">{returnData.return_number}</h1>
            <p className="text-muted-foreground">
              {returnData.reporting_period} - {returnData.financial_year}
            </p>
          </div>
          {getStatusBadge(returnData.status)}
        </div>

        <div className="flex gap-2">
          {returnData.status === 'draft' && (
            <>
              <Button variant="outline" onClick={() => setIsEditing(!isEditing)}>
                {isEditing ? 'Cancel Edit' : 'Edit'}
              </Button>
              <Button onClick={handleApprove}>
                <CheckCircle className="h-4 w-4 mr-2" />
                Approve
              </Button>
            </>
          )}
          {returnData.status === 'approved' && (
            <Button onClick={handleSubmit}>
              <Send className="h-4 w-4 mr-2" />
              Submit to RBI
            </Button>
          )}
          {returnData.excel_file_url && (
            <Button variant="outline">
              <Download className="h-4 w-4 mr-2" />
              Download
            </Button>
          )}
        </div>
      </div>

      {/* Key Metrics */}
      <div className="grid gap-4 md:grid-cols-4">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Total Assets</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {formatCurrency(returnData.total_assets)}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Net Loans</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {formatCurrency(returnData.net_loans_advances)}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">NPA Ratio</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {returnData.npa_ratio.toFixed(2)}%
            </div>
            {returnData.npa_ratio > 5 && (
              <p className="text-xs text-red-600 mt-1">Above threshold</p>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">CRAR</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {returnData.crar_percentage.toFixed(2)}%
            </div>
            {returnData.crar_percentage < 15 && (
              <p className="text-xs text-red-600 mt-1">Below minimum</p>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Tabs */}
      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList>
          <TabsTrigger value="overview">Overview</TabsTrigger>
          <TabsTrigger value="balance-sheet">Balance Sheet</TabsTrigger>
          <TabsTrigger value="income-statement">Income Statement</TabsTrigger>
          <TabsTrigger value="prudential">Prudential Norms</TabsTrigger>
          <TabsTrigger value="timeline">Timeline</TabsTrigger>
        </TabsList>

        {/* Overview Tab */}
        <TabsContent value="overview">
          <div className="grid gap-4 md:grid-cols-2">
            <Card>
              <CardHeader>
                <CardTitle>Return Information</CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <div className="flex justify-between text-sm">
                  <span className="text-muted-foreground">Return Number:</span>
                  <span className="font-medium">{returnData.return_number}</span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-muted-foreground">Reporting Period:</span>
                  <span className="font-medium">{returnData.reporting_period}</span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-muted-foreground">Financial Year:</span>
                  <span className="font-medium">{returnData.financial_year}</span>
                </div>
                {returnData.quarter && (
                  <div className="flex justify-between text-sm">
                    <span className="text-muted-foreground">Quarter:</span>
                    <span className="font-medium">{returnData.quarter}</span>
                  </div>
                )}
                <div className="flex justify-between text-sm">
                  <span className="text-muted-foreground">Period:</span>
                  <span className="font-medium">
                    {formatDate(returnData.period_start_date)} to{' '}
                    {formatDate(returnData.period_end_date)}
                  </span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-muted-foreground">Due Date:</span>
                  <span className="font-medium">{formatDate(returnData.due_date)}</span>
                </div>
                {returnData.is_overdue && (
                  <div className="flex justify-between text-sm">
                    <span className="text-muted-foreground">Days Overdue:</span>
                    <Badge variant="destructive">{returnData.days_overdue} days</Badge>
                  </div>
                )}
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Submission Status</CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                {returnData.prepared_date && (
                  <div className="flex justify-between text-sm">
                    <span className="text-muted-foreground">Prepared:</span>
                    <span className="font-medium">
                      {formatDate(returnData.prepared_date)}
                    </span>
                  </div>
                )}
                {returnData.approved_date && (
                  <div className="flex justify-between text-sm">
                    <span className="text-muted-foreground">Approved:</span>
                    <span className="font-medium">
                      {formatDate(returnData.approved_date)}
                    </span>
                  </div>
                )}
                {returnData.submitted_date && (
                  <div className="flex justify-between text-sm">
                    <span className="text-muted-foreground">Submitted:</span>
                    <span className="font-medium">
                      {formatDate(returnData.submitted_date)}
                    </span>
                  </div>
                )}
                {returnData.submission_reference && (
                  <div className="flex justify-between text-sm">
                    <span className="text-muted-foreground">Reference:</span>
                    <span className="font-medium">{returnData.submission_reference}</span>
                  </div>
                )}
                {returnData.acknowledgement_number && (
                  <div className="flex justify-between text-sm">
                    <span className="text-muted-foreground">Ack. Number:</span>
                    <span className="font-medium">
                      {returnData.acknowledgement_number}
                    </span>
                  </div>
                )}
              </CardContent>
            </Card>
          </div>

          {isEditing && (
            <Card className="mt-4">
              <CardHeader>
                <CardTitle>Edit Remarks</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="space-y-2">
                  <Label htmlFor="remarks">Remarks</Label>
                  <Textarea
                    id="remarks"
                    value={remarks || returnData.remarks || ''}
                    onChange={(e) => setRemarks(e.target.value)}
                    rows={4}
                  />
                </div>
                <Button onClick={handleSave} disabled={updateMutation.isPending}>
                  <Save className="h-4 w-4 mr-2" />
                  {updateMutation.isPending ? 'Saving...' : 'Save Changes'}
                </Button>
              </CardContent>
            </Card>
          )}
        </TabsContent>

        {/* Balance Sheet Tab */}
        <TabsContent value="balance-sheet">
          <div className="grid gap-4 md:grid-cols-2">
            <Card>
              <CardHeader>
                <CardTitle>Assets</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  <div className="flex justify-between text-sm">
                    <span>Total Loans</span>
                    <span className="font-medium">
                      {formatCurrency(returnData.total_loans)}
                    </span>
                  </div>
                  <div className="flex justify-between text-sm pl-4">
                    <span className="text-muted-foreground">Less: Provisions</span>
                    <span className="text-red-600">
                      ({formatCurrency(returnData.total_provisions)})
                    </span>
                  </div>
                  <div className="flex justify-between text-sm font-medium border-t pt-2">
                    <span>Net Loans & Advances</span>
                    <span>{formatCurrency(returnData.net_loans_advances)}</span>
                  </div>

                  <div className="flex justify-between text-sm pt-2">
                    <span>Total Investments</span>
                    <span className="font-medium">
                      {formatCurrency(returnData.total_investments)}
                    </span>
                  </div>

                  <div className="flex justify-between text-sm">
                    <span>Fixed Assets (Net)</span>
                    <span className="font-medium">
                      {formatCurrency(returnData.fixed_assets_net)}
                    </span>
                  </div>

                  <div className="flex justify-between text-sm">
                    <span>Cash & Bank</span>
                    <span className="font-medium">
                      {formatCurrency(returnData.cash_bank_balances)}
                    </span>
                  </div>

                  <div className="flex justify-between text-sm font-bold border-t pt-2 text-lg">
                    <span>Total Assets</span>
                    <span>{formatCurrency(returnData.total_assets)}</span>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Liabilities</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  <div className="flex justify-between text-sm">
                    <span>Share Capital</span>
                    <span className="font-medium">
                      {formatCurrency(returnData.share_capital)}
                    </span>
                  </div>

                  <div className="flex justify-between text-sm">
                    <span>Reserves & Surplus</span>
                    <span className="font-medium">
                      {formatCurrency(returnData.reserves_surplus)}
                    </span>
                  </div>

                  <div className="flex justify-between text-sm font-medium border-t pt-2">
                    <span>Capital & Reserves</span>
                    <span>{formatCurrency(returnData.total_capital_reserves)}</span>
                  </div>

                  <div className="flex justify-between text-sm pt-2">
                    <span>Total Borrowings</span>
                    <span className="font-medium">
                      {formatCurrency(returnData.total_borrowings)}
                    </span>
                  </div>

                  <div className="flex justify-between text-sm">
                    <span>Public Deposits</span>
                    <span className="font-medium">
                      {formatCurrency(returnData.public_deposits)}
                    </span>
                  </div>

                  <div className="flex justify-between text-sm font-bold border-t pt-2 text-lg">
                    <span>Total Liabilities</span>
                    <span>{formatCurrency(returnData.total_liabilities)}</span>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        {/* Income Statement Tab */}
        <TabsContent value="income-statement">
          <Card>
            <CardHeader>
              <CardTitle>Profit & Loss Statement</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-3 max-w-2xl">
                <div className="flex justify-between text-sm font-medium">
                  <span>Income</span>
                  <span>{formatCurrency(returnData.total_income)}</span>
                </div>

                <div className="flex justify-between text-sm font-medium">
                  <span>Expenditure</span>
                  <span className="text-red-600">
                    ({formatCurrency(returnData.total_expenditure)})
                  </span>
                </div>

                <div className="flex justify-between text-sm font-bold border-t pt-2">
                  <span>Profit Before Tax</span>
                  <span
                    className={
                      returnData.profit_before_tax >= 0 ? 'text-green-600' : 'text-red-600'
                    }
                  >
                    {formatCurrency(returnData.profit_before_tax)}
                  </span>
                </div>

                <div className="flex justify-between text-sm">
                  <span>Tax Provision</span>
                  <span className="text-red-600">
                    ({formatCurrency(returnData.tax_provision)})
                  </span>
                </div>

                <div className="flex justify-between text-sm font-bold border-t pt-2 text-lg">
                  <span>Profit After Tax</span>
                  <span
                    className={
                      returnData.profit_after_tax >= 0 ? 'text-green-600' : 'text-red-600'
                    }
                  >
                    {formatCurrency(returnData.profit_after_tax)}
                  </span>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Prudential Norms Tab */}
        <TabsContent value="prudential">
          <div className="grid gap-4 md:grid-cols-2">
            <Card>
              <CardHeader>
                <CardTitle>NPA Analysis</CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <div className="flex justify-between text-sm">
                  <span>Gross NPA</span>
                  <span className="font-medium text-red-600">
                    {formatCurrency(returnData.gross_npa)}
                  </span>
                </div>

                <div className="flex justify-between text-sm">
                  <span>Net NPA</span>
                  <span className="font-medium text-red-600">
                    {formatCurrency(returnData.net_npa)}
                  </span>
                </div>

                <div className="flex justify-between text-sm font-bold border-t pt-2">
                  <span>NPA Ratio</span>
                  <Badge
                    variant={returnData.npa_ratio > 5 ? 'destructive' : 'secondary'}
                    className="text-base"
                  >
                    {returnData.npa_ratio.toFixed(2)}%
                  </Badge>
                </div>

                {returnData.npa_ratio > 5 && (
                  <div className="rounded-lg border p-3 bg-red-50">
                    <div className="flex items-center gap-2">
                      <AlertCircle className="h-4 w-4 text-red-600" />
                      <p className="text-sm text-red-900 font-medium">
                        NPA ratio exceeds RBI threshold of 5%
                      </p>
                    </div>
                  </div>
                )}
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Capital Adequacy (CRAR)</CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <div className="flex justify-between text-sm">
                  <span>Tier 1 Capital</span>
                  <span className="font-medium">
                    {formatCurrency(returnData.tier1_capital)}
                  </span>
                </div>

                <div className="flex justify-between text-sm">
                  <span>Tier 2 Capital</span>
                  <span className="font-medium">
                    {formatCurrency(returnData.tier2_capital)}
                  </span>
                </div>

                <div className="flex justify-between text-sm font-medium border-t pt-2">
                  <span>Total Capital</span>
                  <span>{formatCurrency(returnData.total_capital)}</span>
                </div>

                <div className="flex justify-between text-sm">
                  <span>Risk Weighted Assets</span>
                  <span className="font-medium">
                    {formatCurrency(returnData.risk_weighted_assets)}
                  </span>
                </div>

                <div className="flex justify-between text-sm font-bold border-t pt-2">
                  <span>CRAR</span>
                  <Badge
                    variant={returnData.crar_percentage < 15 ? 'destructive' : 'secondary'}
                    className="text-base"
                  >
                    {returnData.crar_percentage.toFixed(2)}%
                  </Badge>
                </div>

                {returnData.crar_percentage < 15 && (
                  <div className="rounded-lg border p-3 bg-red-50">
                    <div className="flex items-center gap-2">
                      <AlertCircle className="h-4 w-4 text-red-600" />
                      <p className="text-sm text-red-900 font-medium">
                        CRAR below minimum requirement of 15%
                      </p>
                    </div>
                  </div>
                )}
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        {/* Timeline Tab */}
        <TabsContent value="timeline">
          <Card>
            <CardHeader>
              <CardTitle>Return Timeline</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {returnData.prepared_date && (
                  <TimelineItem
                    date={returnData.prepared_date}
                    title="Return Prepared"
                    description="Auto-generated from system data"
                    icon={<FileText className="h-4 w-4" />}
                  />
                )}
                {returnData.approved_date && (
                  <TimelineItem
                    date={returnData.approved_date}
                    title="Return Approved"
                    description="Approved by manager"
                    icon={<CheckCircle className="h-4 w-4" />}
                  />
                )}
                {returnData.submitted_date && (
                  <TimelineItem
                    date={returnData.submitted_date}
                    title="Submitted to RBI"
                    description={`Reference: ${returnData.submission_reference}`}
                    icon={<Send className="h-4 w-4" />}
                  />
                )}
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  )
}

function TimelineItem({
  date,
  title,
  description,
  icon,
}: {
  date: string
  title: string
  description: string
  icon: React.ReactNode
}) {
  return (
    <div className="flex gap-4">
      <div className="flex flex-col items-center">
        <div className="flex h-8 w-8 items-center justify-center rounded-full bg-primary text-primary-foreground">
          {icon}
        </div>
        <div className="h-full w-px bg-border" />
      </div>
      <div className="flex-1 pb-8">
        <p className="text-sm font-medium">{title}</p>
        <p className="text-xs text-muted-foreground">{formatDate(date)}</p>
        <p className="text-sm text-muted-foreground mt-1">{description}</p>
      </div>
    </div>
  )
}

function PageSkeleton() {
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <Skeleton className="h-8 w-64" />
        <Skeleton className="h-10 w-32" />
      </div>

      <div className="grid gap-4 md:grid-cols-4">
        {[1, 2, 3, 4].map((i) => (
          <Card key={i}>
            <CardHeader>
              <Skeleton className="h-4 w-24" />
            </CardHeader>
            <CardContent>
              <Skeleton className="h-8 w-32" />
            </CardContent>
          </Card>
        ))}
      </div>

      <Card>
        <CardHeader>
          <Skeleton className="h-6 w-48" />
        </CardHeader>
        <CardContent>
          <Skeleton className="h-96 w-full" />
        </CardContent>
      </Card>
    </div>
  )
}
