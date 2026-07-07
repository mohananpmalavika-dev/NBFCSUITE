'use client'

/**
 * NBS-7 Returns Management Page
 * List, generate, and manage NBS-7 monthly/quarterly returns
 */

import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Badge } from '@/components/ui/badge'
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { Label } from '@/components/ui/label'
import {
  Plus,
  Search,
  Filter,
  Eye,
  CheckCircle,
  Send,
  Download,
  Calendar,
  FileText,
} from 'lucide-react'
import { rbiReturnsService } from '@/services/rbi-returns.service'
import { formatCurrency, formatDate } from '@/lib/utils'
import { toast } from '@/components/ui/use-toast'
import { Skeleton } from '@/components/ui/skeleton'
import Link from 'next/link'
import type { NBS7ReturnGenerateRequest } from '@/types/rbi-returns.types'

export default function NBS7ReturnsPage() {
  const queryClient = useQueryClient()
  const [generateDialogOpen, setGenerateDialogOpen] = useState(false)
  const [searchTerm, setSearchTerm] = useState('')
  const [selectedYear, setSelectedYear] = useState<string>('')
  const [selectedQuarter, setSelectedQuarter] = useState<string>('')
  const [selectedStatus, setSelectedStatus] = useState<string>('')

  // Generate form state
  const [reportingPeriod, setReportingPeriod] = useState('')
  const [periodStartDate, setPeriodStartDate] = useState('')
  const [periodEndDate, setPeriodEndDate] = useState('')
  const [asOnDate, setAsOnDate] = useState('')
  const [financialYear, setFinancialYear] = useState('FY2024-25')
  const [quarter, setQuarter] = useState<string>('')
  const [remarks, setRemarks] = useState('')

  // Fetch NBS-7 returns
  const { data: returns, isLoading, refetch } = useQuery({
    queryKey: ['nbs7-returns', selectedYear, selectedQuarter, selectedStatus],
    queryFn: () =>
      rbiReturnsService.listNBS7Returns({
        financial_year: selectedYear || undefined,
        quarter: selectedQuarter || undefined,
        status: selectedStatus || undefined,
        limit: 50,
      }),
  })

  // Generate NBS-7 return mutation
  const generateMutation = useMutation({
    mutationFn: (request: NBS7ReturnGenerateRequest) =>
      rbiReturnsService.generateNBS7Return(request),
    onSuccess: () => {
      toast({
        title: 'NBS-7 Return Generated',
        description: 'Return has been generated successfully from system data',
      })
      setGenerateDialogOpen(false)
      resetGenerateForm()
      queryClient.invalidateQueries({ queryKey: ['nbs7-returns'] })
    },
    onError: (error: any) => {
      toast({
        title: 'Generation Failed',
        description: error.response?.data?.error?.message || 'Failed to generate return',
        variant: 'destructive',
      })
    },
  })

  // Approve mutation
  const approveMutation = useMutation({
    mutationFn: (id: string) => rbiReturnsService.approveNBS7Return(id),
    onSuccess: () => {
      toast({
        title: 'Return Approved',
        description: 'NBS-7 return has been approved successfully',
      })
      queryClient.invalidateQueries({ queryKey: ['nbs7-returns'] })
    },
  })

  // Submit mutation
  const submitMutation = useMutation({
    mutationFn: ({ id, reference }: { id: string; reference: string }) =>
      rbiReturnsService.submitNBS7Return(id, reference),
    onSuccess: () => {
      toast({
        title: 'Return Submitted',
        description: 'NBS-7 return has been submitted to RBI',
      })
      queryClient.invalidateQueries({ queryKey: ['nbs7-returns'] })
    },
  })

  const handleGenerate = () => {
    if (!reportingPeriod || !periodStartDate || !periodEndDate || !asOnDate) {
      toast({
        title: 'Validation Error',
        description: 'Please fill all required fields',
        variant: 'destructive',
      })
      return
    }

    const request: NBS7ReturnGenerateRequest = {
      reporting_period: reportingPeriod,
      period_start_date: periodStartDate,
      period_end_date: periodEndDate,
      as_on_date: asOnDate,
      financial_year: financialYear,
      quarter: quarter || undefined,
      include_sectoral: true,
      include_geographic: true,
      remarks: remarks || undefined,
    }

    generateMutation.mutate(request)
  }

  const handleApprove = (id: string, returnNumber: string) => {
    if (confirm(`Are you sure you want to approve return ${returnNumber}?`)) {
      approveMutation.mutate(id)
    }
  }

  const handleSubmit = (id: string, returnNumber: string) => {
    const reference = prompt(`Enter RBI submission reference for ${returnNumber}:`)
    if (reference) {
      submitMutation.mutate({ id, reference })
    }
  }

  const resetGenerateForm = () => {
    setReportingPeriod('')
    setPeriodStartDate('')
    setPeriodEndDate('')
    setAsOnDate('')
    setQuarter('')
    setRemarks('')
  }

  const getStatusBadge = (status: string) => {
    const variants: Record<string, any> = {
      draft: 'secondary',
      pending_review: 'default',
      approved: 'default',
      submitted: 'default',
      rejected: 'destructive',
    }

    const colors: Record<string, string> = {
      draft: 'bg-gray-100 text-gray-800',
      pending_review: 'bg-blue-100 text-blue-800',
      approved: 'bg-green-100 text-green-800',
      submitted: 'bg-purple-100 text-purple-800',
      rejected: 'bg-red-100 text-red-800',
    }

    return (
      <Badge className={colors[status] || 'bg-gray-100'}>
        {status.replace('_', ' ').toUpperCase()}
      </Badge>
    )
  }

  const filteredReturns = returns?.filter((ret: any) => {
    if (searchTerm) {
      return (
        ret.return_number.toLowerCase().includes(searchTerm.toLowerCase()) ||
        ret.reporting_period.toLowerCase().includes(searchTerm.toLowerCase())
      )
    }
    return true
  })

  if (isLoading) {
    return <PageSkeleton />
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">NBS-7 Returns</h1>
          <p className="text-muted-foreground">
            Monthly and quarterly financial returns to RBI
          </p>
        </div>
        <Button onClick={() => setGenerateDialogOpen(true)}>
          <Plus className="h-4 w-4 mr-2" />
          Generate New Return
        </Button>
      </div>

      {/* Filters */}
      <Card>
        <CardContent className="pt-6">
          <div className="grid gap-4 md:grid-cols-5">
            <div className="relative">
              <Search className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
              <Input
                placeholder="Search returns..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-9"
              />
            </div>

            <Select value={selectedYear} onValueChange={setSelectedYear}>
              <SelectTrigger>
                <SelectValue placeholder="Financial Year" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="">All Years</SelectItem>
                <SelectItem value="FY2024-25">FY 2024-25</SelectItem>
                <SelectItem value="FY2023-24">FY 2023-24</SelectItem>
                <SelectItem value="FY2022-23">FY 2022-23</SelectItem>
              </SelectContent>
            </Select>

            <Select value={selectedQuarter} onValueChange={setSelectedQuarter}>
              <SelectTrigger>
                <SelectValue placeholder="Quarter" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="">All Quarters</SelectItem>
                <SelectItem value="Q1">Q1</SelectItem>
                <SelectItem value="Q2">Q2</SelectItem>
                <SelectItem value="Q3">Q3</SelectItem>
                <SelectItem value="Q4">Q4</SelectItem>
              </SelectContent>
            </Select>

            <Select value={selectedStatus} onValueChange={setSelectedStatus}>
              <SelectTrigger>
                <SelectValue placeholder="Status" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="">All Status</SelectItem>
                <SelectItem value="draft">Draft</SelectItem>
                <SelectItem value="pending_review">Pending Review</SelectItem>
                <SelectItem value="approved">Approved</SelectItem>
                <SelectItem value="submitted">Submitted</SelectItem>
              </SelectContent>
            </Select>

            <Button variant="outline" onClick={() => refetch()}>
              <Filter className="h-4 w-4 mr-2" />
              Refresh
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Returns Table */}
      <Card>
        <CardHeader>
          <CardTitle>NBS-7 Returns List</CardTitle>
        </CardHeader>
        <CardContent>
          {filteredReturns?.length === 0 ? (
            <div className="text-center py-12">
              <FileText className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
              <p className="text-muted-foreground">
                No NBS-7 returns found. Generate your first return to get started.
              </p>
              <Button onClick={() => setGenerateDialogOpen(true)} className="mt-4">
                <Plus className="h-4 w-4 mr-2" />
                Generate New Return
              </Button>
            </div>
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Return Number</TableHead>
                  <TableHead>Period</TableHead>
                  <TableHead>Financial Year</TableHead>
                  <TableHead className="text-right">Total Assets</TableHead>
                  <TableHead className="text-right">NPA Ratio</TableHead>
                  <TableHead className="text-right">CRAR</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead>Due Date</TableHead>
                  <TableHead className="text-right">Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {filteredReturns?.map((returnItem: any) => (
                  <TableRow key={returnItem.id}>
                    <TableCell className="font-medium">
                      {returnItem.return_number}
                    </TableCell>
                    <TableCell>
                      <div>
                        <div className="font-medium">{returnItem.reporting_period}</div>
                        {returnItem.quarter && (
                          <div className="text-xs text-muted-foreground">
                            {returnItem.quarter}
                          </div>
                        )}
                      </div>
                    </TableCell>
                    <TableCell>{returnItem.financial_year}</TableCell>
                    <TableCell className="text-right">
                      {formatCurrency(returnItem.total_assets)}
                    </TableCell>
                    <TableCell className="text-right">
                      <Badge
                        variant={returnItem.npa_ratio > 5 ? 'destructive' : 'secondary'}
                      >
                        {returnItem.npa_ratio.toFixed(2)}%
                      </Badge>
                    </TableCell>
                    <TableCell className="text-right">
                      <Badge
                        variant={returnItem.crar_percentage < 15 ? 'destructive' : 'secondary'}
                      >
                        {returnItem.crar_percentage.toFixed(2)}%
                      </Badge>
                    </TableCell>
                    <TableCell>{getStatusBadge(returnItem.status)}</TableCell>
                    <TableCell>
                      <div className="flex items-center gap-2">
                        <Calendar className="h-4 w-4 text-muted-foreground" />
                        <span>{formatDate(returnItem.due_date)}</span>
                      </div>
                      {returnItem.is_overdue && (
                        <Badge variant="destructive" className="text-xs mt-1">
                          {returnItem.days_overdue} days overdue
                        </Badge>
                      )}
                    </TableCell>
                    <TableCell className="text-right">
                      <div className="flex items-center justify-end gap-2">
                        <Link href={`/rbi-returns/nbs7/${returnItem.id}`}>
                          <Button size="sm" variant="ghost">
                            <Eye className="h-4 w-4" />
                          </Button>
                        </Link>

                        {returnItem.status === 'draft' && (
                          <Button
                            size="sm"
                            variant="outline"
                            onClick={() =>
                              handleApprove(returnItem.id, returnItem.return_number)
                            }
                          >
                            <CheckCircle className="h-4 w-4 mr-1" />
                            Approve
                          </Button>
                        )}

                        {returnItem.status === 'approved' && (
                          <Button
                            size="sm"
                            onClick={() =>
                              handleSubmit(returnItem.id, returnItem.return_number)
                            }
                          >
                            <Send className="h-4 w-4 mr-1" />
                            Submit
                          </Button>
                        )}

                        {returnItem.excel_file_url && (
                          <Button size="sm" variant="ghost">
                            <Download className="h-4 w-4" />
                          </Button>
                        )}
                      </div>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          )}
        </CardContent>
      </Card>

      {/* Generate Dialog */}
      <Dialog open={generateDialogOpen} onOpenChange={setGenerateDialogOpen}>
        <DialogContent className="max-w-2xl">
          <DialogHeader>
            <DialogTitle>Generate NBS-7 Return</DialogTitle>
            <DialogDescription>
              Auto-generate NBS-7 return from system data (loans, deposits, GL accounts)
            </DialogDescription>
          </DialogHeader>

          <div className="grid gap-4 py-4">
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="reporting_period">
                  Reporting Period <span className="text-red-500">*</span>
                </Label>
                <Input
                  id="reporting_period"
                  placeholder="2024-06"
                  value={reportingPeriod}
                  onChange={(e) => setReportingPeriod(e.target.value)}
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="financial_year">
                  Financial Year <span className="text-red-500">*</span>
                </Label>
                <Select value={financialYear} onValueChange={setFinancialYear}>
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="FY2024-25">FY 2024-25</SelectItem>
                    <SelectItem value="FY2023-24">FY 2023-24</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>

            <div className="grid grid-cols-3 gap-4">
              <div className="space-y-2">
                <Label htmlFor="period_start">
                  Period Start <span className="text-red-500">*</span>
                </Label>
                <Input
                  id="period_start"
                  type="date"
                  value={periodStartDate}
                  onChange={(e) => setPeriodStartDate(e.target.value)}
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="period_end">
                  Period End <span className="text-red-500">*</span>
                </Label>
                <Input
                  id="period_end"
                  type="date"
                  value={periodEndDate}
                  onChange={(e) => setPeriodEndDate(e.target.value)}
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="as_on_date">
                  As On Date <span className="text-red-500">*</span>
                </Label>
                <Input
                  id="as_on_date"
                  type="date"
                  value={asOnDate}
                  onChange={(e) => setAsOnDate(e.target.value)}
                />
              </div>
            </div>

            <div className="space-y-2">
              <Label htmlFor="quarter">Quarter (Optional)</Label>
              <Select value={quarter} onValueChange={setQuarter}>
                <SelectTrigger>
                  <SelectValue placeholder="Select quarter if applicable" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="">Not Applicable</SelectItem>
                  <SelectItem value="Q1">Q1</SelectItem>
                  <SelectItem value="Q2">Q2</SelectItem>
                  <SelectItem value="Q3">Q3</SelectItem>
                  <SelectItem value="Q4">Q4</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-2">
              <Label htmlFor="remarks">Remarks (Optional)</Label>
              <Input
                id="remarks"
                placeholder="Any additional notes"
                value={remarks}
                onChange={(e) => setRemarks(e.target.value)}
              />
            </div>

            <div className="rounded-lg border p-4 bg-blue-50">
              <p className="text-sm text-blue-900 font-medium mb-2">Auto-Generated Data:</p>
              <ul className="text-xs text-blue-700 space-y-1">
                <li>✓ Loan balances from Loan Management System</li>
                <li>✓ Deposit balances from Deposit Management</li>
                <li>✓ GL balances from General Ledger</li>
                <li>✓ NPA calculation (DPD {'>'} 90 days)</li>
                <li>✓ CRAR and prudential ratios</li>
              </ul>
            </div>
          </div>

          <DialogFooter>
            <Button
              variant="outline"
              onClick={() => setGenerateDialogOpen(false)}
              disabled={generateMutation.isPending}
            >
              Cancel
            </Button>
            <Button onClick={handleGenerate} disabled={generateMutation.isPending}>
              {generateMutation.isPending ? 'Generating...' : 'Generate Return'}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  )
}

function PageSkeleton() {
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div className="space-y-2">
          <Skeleton className="h-8 w-64" />
          <Skeleton className="h-4 w-96" />
        </div>
        <Skeleton className="h-10 w-48" />
      </div>

      <Card>
        <CardContent className="pt-6">
          <div className="grid gap-4 md:grid-cols-5">
            {[1, 2, 3, 4, 5].map((i) => (
              <Skeleton key={i} className="h-10" />
            ))}
          </div>
        </CardContent>
      </Card>

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
