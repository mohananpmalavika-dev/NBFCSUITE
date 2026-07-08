'use client'

/**
 * Statutory Returns Management Page
 * Manage all RBI statutory returns (ALM, LCR, NSFR, etc.)
 */

import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Badge } from '@/components/ui/badge'
import { Textarea } from '@/components/ui/textarea'
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
  Edit,
} from 'lucide-react'
import { rbiReturnsService } from '@/services/rbi-returns.service'
import { formatDate } from '@/lib/utils'
import { toast } from '@/components/ui/use-toast'
import { Skeleton } from '@/components/ui/skeleton'
import type { CreateStatutoryReturnRequest } from '@/types/rbi-returns.types'

export default function StatutoryReturnsPage() {
  const queryClient = useQueryClient()
  const [createDialogOpen, setCreateDialogOpen] = useState(false)
  const [viewDialogOpen, setViewDialogOpen] = useState(false)
  const [selectedReturn, setSelectedReturn] = useState<any>(null)
  const [searchTerm, setSearchTerm] = useState('')
  const [selectedReturnType, setSelectedReturnType] = useState<string>('')
  const [selectedStatus, setSelectedStatus] = useState<string>('')

  // Create form state
  const [returnType, setReturnType] = useState('')
  const [reportingPeriod, setReportingPeriod] = useState('')
  const [periodStartDate, setPeriodStartDate] = useState('')
  const [periodEndDate, setPeriodEndDate] = useState('')
  const [dueDate, setDueDate] = useState('')
  const [returnData, setReturnData] = useState('')
  const [remarks, setRemarks] = useState('')

  // Fetch statutory returns
  const { data: returns, isLoading, refetch } = useQuery({
    queryKey: ['statutory-returns', selectedReturnType, selectedStatus],
    queryFn: () =>
      rbiReturnsService.listStatutoryReturns({
        return_type: selectedReturnType || undefined,
        status: selectedStatus || undefined,
        limit: 50,
      }),
  })

  // Create statutory return mutation
  const createMutation = useMutation({
    mutationFn: (request: CreateStatutoryReturnRequest) =>
      rbiReturnsService.createStatutoryReturn(request),
    onSuccess: () => {
      toast({
        title: 'Statutory Return Created',
        description: 'Return has been created successfully',
      })
      setCreateDialogOpen(false)
      resetCreateForm()
      queryClient.invalidateQueries({ queryKey: ['statutory-returns'] })
    },
    onError: (error: any) => {
      toast({
        title: 'Creation Failed',
        description: error.response?.data?.error?.message || 'Failed to create return',
        variant: 'destructive',
      })
    },
  })

  // Approve mutation
  const approveMutation = useMutation({
    mutationFn: (id: string) => rbiReturnsService.approveStatutoryReturn(id),
    onSuccess: () => {
      toast({
        title: 'Return Approved',
        description: 'Statutory return has been approved successfully',
      })
      queryClient.invalidateQueries({ queryKey: ['statutory-returns'] })
    },
  })

  // Submit mutation
  const submitMutation = useMutation({
    mutationFn: ({ id, reference }: { id: string; reference: string }) =>
      rbiReturnsService.submitStatutoryReturn(id, reference),
    onSuccess: () => {
      toast({
        title: 'Return Submitted',
        description: 'Statutory return has been submitted to RBI',
      })
      queryClient.invalidateQueries({ queryKey: ['statutory-returns'] })
    },
  })

  const handleCreate = () => {
    if (!returnType || !reportingPeriod || !dueDate || !returnData) {
      toast({
        title: 'Validation Error',
        description: 'Please fill all required fields',
        variant: 'destructive',
      })
      return
    }

    // Parse JSON data
    let parsedData
    try {
      parsedData = JSON.parse(returnData)
    } catch (e) {
      toast({
        title: 'Invalid JSON',
        description: 'Return data must be valid JSON',
        variant: 'destructive',
      })
      return
    }

    const request: CreateStatutoryReturnRequest = {
      return_master_id: '', // Will be handled by backend
      return_type: returnType,
      reporting_period: reportingPeriod,
      period_start_date: periodStartDate,
      period_end_date: periodEndDate,
      as_on_date: periodEndDate,
      financial_year: new Date(periodEndDate).getFullYear().toString(),
      return_data: parsedData,
      remarks: remarks || undefined,
    }

    createMutation.mutate(request)
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

  const handleViewDetails = (returnItem: any) => {
    setSelectedReturn(returnItem)
    setViewDialogOpen(true)
  }

  const resetCreateForm = () => {
    setReturnType('')
    setReportingPeriod('')
    setPeriodStartDate('')
    setPeriodEndDate('')
    setDueDate('')
    setReturnData('')
    setRemarks('')
  }

  const getStatusBadge = (status: string) => {
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

  const getReturnTypeBadge = (type: string) => {
    const colors: Record<string, string> = {
      alm_return: 'bg-blue-50 text-blue-700',
      lcr_return: 'bg-green-50 text-green-700',
      nsfr_return: 'bg-purple-50 text-purple-700',
      fraud_reporting: 'bg-red-50 text-red-700',
      kyc_aml_return: 'bg-yellow-50 text-yellow-700',
      other: 'bg-gray-50 text-gray-700',
    }

    return (
      <Badge variant="outline" className={colors[type] || 'bg-gray-50'}>
        {type.replace('_', ' ').toUpperCase()}
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
          <h1 className="text-3xl font-bold">Statutory Returns</h1>
          <p className="text-muted-foreground">
            Manage all RBI statutory returns (ALM, LCR, NSFR, Fraud, KYC/AML)
          </p>
        </div>
        <Button onClick={() => setCreateDialogOpen(true)}>
          <Plus className="h-4 w-4 mr-2" />
          Create New Return
        </Button>
      </div>

      {/* Statistics Cards */}
      <div className="grid gap-4 md:grid-cols-4">
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium text-muted-foreground">
              Total Returns
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{returns?.length || 0}</div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium text-muted-foreground">
              Pending Review
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {returns?.filter((r: any) => r.status === 'pending_review').length || 0}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium text-muted-foreground">
              Approved
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {returns?.filter((r: any) => r.status === 'approved').length || 0}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium text-muted-foreground">
              Submitted
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {returns?.filter((r: any) => r.status === 'submitted').length || 0}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Filters */}
      <Card>
        <CardContent className="pt-6">
          <div className="grid gap-4 md:grid-cols-4">
            <div className="relative">
              <Search className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
              <Input
                placeholder="Search returns..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-9"
              />
            </div>

            <Select value={selectedReturnType} onValueChange={setSelectedReturnType}>
              <SelectTrigger>
                <SelectValue placeholder="Return Type" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="">All Types</SelectItem>
                <SelectItem value="alm_return">ALM Return</SelectItem>
                <SelectItem value="lcr_return">LCR Return</SelectItem>
                <SelectItem value="nsfr_return">NSFR Return</SelectItem>
                <SelectItem value="fraud_reporting">Fraud Reporting</SelectItem>
                <SelectItem value="kyc_aml_return">KYC/AML Return</SelectItem>
                <SelectItem value="other">Other</SelectItem>
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
          <CardTitle>Statutory Returns List</CardTitle>
        </CardHeader>
        <CardContent>
          {filteredReturns?.length === 0 ? (
            <div className="text-center py-12">
              <FileText className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
              <p className="text-muted-foreground">
                No statutory returns found. Create your first return to get started.
              </p>
              <Button onClick={() => setCreateDialogOpen(true)} className="mt-4">
                <Plus className="h-4 w-4 mr-2" />
                Create New Return
              </Button>
            </div>
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Return Number</TableHead>
                  <TableHead>Type</TableHead>
                  <TableHead>Reporting Period</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead>Due Date</TableHead>
                  <TableHead>Submitted Date</TableHead>
                  <TableHead className="text-right">Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {filteredReturns?.map((returnItem: any) => (
                  <TableRow key={returnItem.id}>
                    <TableCell className="font-medium">
                      {returnItem.return_number}
                    </TableCell>
                    <TableCell>{getReturnTypeBadge(returnItem.return_type)}</TableCell>
                    <TableCell>{returnItem.reporting_period}</TableCell>
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
                    <TableCell>
                      {returnItem.submitted_date
                        ? formatDate(returnItem.submitted_date)
                        : '-'}
                    </TableCell>
                    <TableCell className="text-right">
                      <div className="flex items-center justify-end gap-2">
                        <Button
                          size="sm"
                          variant="ghost"
                          onClick={() => handleViewDetails(returnItem)}
                        >
                          <Eye className="h-4 w-4" />
                        </Button>

                        {returnItem.status === 'draft' && (
                          <>
                            <Button size="sm" variant="ghost">
                              <Edit className="h-4 w-4" />
                            </Button>
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
                          </>
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

                        {returnItem.pdf_file_url && (
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

      {/* Create Dialog */}
      <Dialog open={createDialogOpen} onOpenChange={setCreateDialogOpen}>
        <DialogContent className="max-w-3xl max-h-[90vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>Create Statutory Return</DialogTitle>
            <DialogDescription>
              Create a new statutory return with custom data structure
            </DialogDescription>
          </DialogHeader>

          <div className="grid gap-4 py-4">
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="return_type">
                  Return Type <span className="text-red-500">*</span>
                </Label>
                <Select value={returnType} onValueChange={setReturnType}>
                  <SelectTrigger>
                    <SelectValue placeholder="Select return type" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="alm_return">ALM Return</SelectItem>
                    <SelectItem value="lcr_return">LCR Return</SelectItem>
                    <SelectItem value="nsfr_return">NSFR Return</SelectItem>
                    <SelectItem value="fraud_reporting">Fraud Reporting</SelectItem>
                    <SelectItem value="kyc_aml_return">KYC/AML Return</SelectItem>
                    <SelectItem value="other">Other</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>

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

            <div className="grid grid-cols-3 gap-4">
              <div className="space-y-2">
                <Label htmlFor="period_start">Period Start</Label>
                <Input
                  id="period_start"
                  type="date"
                  value={periodStartDate}
                  onChange={(e) => setPeriodStartDate(e.target.value)}
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="period_end">Period End</Label>
                <Input
                  id="period_end"
                  type="date"
                  value={periodEndDate}
                  onChange={(e) => setPeriodEndDate(e.target.value)}
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="due_date">
                  Due Date <span className="text-red-500">*</span>
                </Label>
                <Input
                  id="due_date"
                  type="date"
                  value={dueDate}
                  onChange={(e) => setDueDate(e.target.value)}
                />
              </div>
            </div>

            <div className="space-y-2">
              <Label htmlFor="return_data">
                Return Data (JSON) <span className="text-red-500">*</span>
              </Label>
              <Textarea
                id="return_data"
                placeholder={`{\n  "field1": "value1",\n  "field2": 1000,\n  "nested": {\n    "field3": true\n  }\n}`}
                value={returnData}
                onChange={(e) => setReturnData(e.target.value)}
                rows={10}
                className="font-mono text-sm"
              />
              <p className="text-xs text-muted-foreground">
                Enter return data as valid JSON. The structure is flexible and depends on the
                return type.
              </p>
            </div>

            <div className="space-y-2">
              <Label htmlFor="remarks">Remarks</Label>
              <Textarea
                id="remarks"
                placeholder="Any additional notes"
                value={remarks}
                onChange={(e) => setRemarks(e.target.value)}
                rows={3}
              />
            </div>

            <div className="rounded-lg border p-4 bg-blue-50">
              <p className="text-sm text-blue-900 font-medium mb-2">
                Common Return Types:
              </p>
              <ul className="text-xs text-blue-700 space-y-1">
                <li>• <strong>ALM Return:</strong> Asset Liability Management reporting</li>
                <li>• <strong>LCR Return:</strong> Liquidity Coverage Ratio</li>
                <li>• <strong>NSFR Return:</strong> Net Stable Funding Ratio</li>
                <li>• <strong>Fraud Reporting:</strong> Fraud cases and incidents</li>
                <li>• <strong>KYC/AML Return:</strong> Know Your Customer and Anti-Money Laundering</li>
              </ul>
            </div>
          </div>

          <DialogFooter>
            <Button
              variant="outline"
              onClick={() => setCreateDialogOpen(false)}
              disabled={createMutation.isPending}
            >
              Cancel
            </Button>
            <Button onClick={handleCreate} disabled={createMutation.isPending}>
              {createMutation.isPending ? 'Creating...' : 'Create Return'}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* View Details Dialog */}
      <Dialog open={viewDialogOpen} onOpenChange={setViewDialogOpen}>
        <DialogContent className="max-w-4xl max-h-[90vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>Return Details</DialogTitle>
            <DialogDescription>
              {selectedReturn?.return_number} - {selectedReturn?.reporting_period}
            </DialogDescription>
          </DialogHeader>

          {selectedReturn && (
            <div className="space-y-6 py-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <Label className="text-muted-foreground">Return Type</Label>
                  <div className="mt-1">{getReturnTypeBadge(selectedReturn.return_type)}</div>
                </div>
                <div>
                  <Label className="text-muted-foreground">Status</Label>
                  <div className="mt-1">{getStatusBadge(selectedReturn.status)}</div>
                </div>
                <div>
                  <Label className="text-muted-foreground">Due Date</Label>
                  <div className="mt-1">{formatDate(selectedReturn.due_date)}</div>
                </div>
                <div>
                  <Label className="text-muted-foreground">Submitted Date</Label>
                  <div className="mt-1">
                    {selectedReturn.submitted_date
                      ? formatDate(selectedReturn.submitted_date)
                      : 'Not submitted'}
                  </div>
                </div>
              </div>

              {selectedReturn.rbi_reference_number && (
                <div>
                  <Label className="text-muted-foreground">RBI Reference Number</Label>
                  <div className="mt-1 font-mono text-sm">
                    {selectedReturn.rbi_reference_number}
                  </div>
                </div>
              )}

              <div>
                <Label className="text-muted-foreground">Return Data</Label>
                <pre className="mt-2 rounded-lg border bg-gray-50 p-4 text-xs overflow-x-auto">
                  {JSON.stringify(selectedReturn.return_data, null, 2)}
                </pre>
              </div>

              {selectedReturn.remarks && (
                <div>
                  <Label className="text-muted-foreground">Remarks</Label>
                  <div className="mt-1 text-sm">{selectedReturn.remarks}</div>
                </div>
              )}

              {selectedReturn.validation_errors && selectedReturn.validation_errors.length > 0 && (
                <div>
                  <Label className="text-muted-foreground text-red-600">
                    Validation Errors
                  </Label>
                  <div className="mt-2 space-y-1">
                    {selectedReturn.validation_errors.map((error: string, idx: number) => (
                      <div key={idx} className="text-sm text-red-600 flex items-start gap-2">
                        <span>•</span>
                        <span>{error}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}

          <DialogFooter>
            <Button variant="outline" onClick={() => setViewDialogOpen(false)}>
              Close
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

      <div className="grid gap-4 md:grid-cols-4">
        {[1, 2, 3, 4].map((i) => (
          <Card key={i}>
            <CardHeader className="pb-3">
              <Skeleton className="h-4 w-24" />
            </CardHeader>
            <CardContent>
              <Skeleton className="h-8 w-16" />
            </CardContent>
          </Card>
        ))}
      </div>

      <Card>
        <CardContent className="pt-6">
          <div className="grid gap-4 md:grid-cols-4">
            {[1, 2, 3, 4].map((i) => (
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
