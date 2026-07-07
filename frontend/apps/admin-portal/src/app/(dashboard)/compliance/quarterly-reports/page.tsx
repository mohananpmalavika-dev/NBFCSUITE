'use client'

/**
 * Quarterly Reports Page
 * Generate and manage CRILC & SMA quarterly reports
 */

import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Badge } from '@/components/ui/badge'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
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
  DialogTrigger,
} from '@/components/ui/dialog'
import { Label } from '@/components/ui/label'
import {
  FileText,
  Plus,
  CheckCircle,
  Send,
  Calendar,
  Download,
  Eye,
} from 'lucide-react'
import { complianceService } from '@/services/compliance.service'
import { formatCurrency, formatDate } from '@/lib/utils'
import type {
  CRILCQuarterlyReturn,
  SMAQuarterlyReport,
  CreateCRILCQuarterlyReturnRequest,
  CreateSMAQuarterlyReportRequest,
} from '@/types/compliance.types'
import { toast } from '@/components/ui/use-toast'
import { Skeleton } from '@/components/ui/skeleton'

export default function QuarterlyReportsPage() {
  const queryClient = useQueryClient()
  const [activeTab, setActiveTab] = useState('crilc')
  const [generateDialogOpen, setGenerateDialogOpen] = useState(false)
  const [reportType, setReportType] = useState<'crilc' | 'sma'>('crilc')
  const [quarter, setQuarter] = useState('Q1FY25')
  const [year, setYear] = useState('FY2024-25')
  const [asOnDate, setAsOnDate] = useState(new Date().toISOString().split('T')[0])
  const [remarks, setRemarks] = useState('')
  const [page, setPage] = useState(1)

  const { data: crilcReturns, isLoading: crilcLoading } = useQuery({
    queryKey: ['crilc-quarterly-returns', page],
    queryFn: () =>
      complianceService.getQuarterlyReturns({
        page: page,
        page_size: 20,
      }),
    enabled: activeTab === 'crilc',
  })

  const generateCRILCMutation = useMutation({
    mutationFn: (data: CreateCRILCQuarterlyReturnRequest) =>
      complianceService.generateQuarterlyReturn(data),
    onSuccess: () => {
      toast({
        title: 'CRILC Return Generated',
        description: 'Quarterly return has been generated successfully',
      })
      setGenerateDialogOpen(false)
      queryClient.invalidateQueries({ queryKey: ['crilc-quarterly-returns'] })
      resetForm()
    },
  })

  const generateSMAMutation = useMutation({
    mutationFn: (data: CreateSMAQuarterlyReportRequest) =>
      complianceService.generateSMAQuarterlyReport(data),
    onSuccess: () => {
      toast({
        title: 'SMA Report Generated',
        description: 'Quarterly report has been generated successfully',
      })
      setGenerateDialogOpen(false)
      resetForm()
    },
  })

  const approveMutation = useMutation({
    mutationFn: (id: string) => complianceService.approveQuarterlyReturn(id),
    onSuccess: () => {
      toast({
        title: 'Return Approved',
        description: 'Quarterly return has been approved',
      })
      queryClient.invalidateQueries({ queryKey: ['crilc-quarterly-returns'] })
    },
  })

  const submitMutation = useMutation({
    mutationFn: ({ id, reference }: { id: string; reference: string }) =>
      complianceService.submitQuarterlyReturn(id, reference),
    onSuccess: () => {
      toast({
        title: 'Return Submitted',
        description: 'Quarterly return has been submitted to RBI',
      })
      queryClient.invalidateQueries({ queryKey: ['crilc-quarterly-returns'] })
    },
  })

  const handleGenerate = () => {
    if (reportType === 'crilc') {
      generateCRILCMutation.mutate({
        reporting_quarter: quarter,
        reporting_year: year,
        as_on_date: asOnDate,
        remarks: remarks || undefined,
      })
    } else {
      generateSMAMutation.mutate({
        reporting_quarter: quarter,
        reporting_year: year,
        as_on_date: asOnDate,
        remarks: remarks || undefined,
      })
    }
  }

  const handleApprove = (id: string) => {
    if (confirm('Are you sure you want to approve this return?')) {
      approveMutation.mutate(id)
    }
  }

  const handleSubmit = (id: string) => {
    const reference = prompt('Enter submission reference number:')
    if (reference) {
      submitMutation.mutate({ id, reference })
    }
  }

  const resetForm = () => {
    setQuarter('Q1FY25')
    setYear('FY2024-25')
    setAsOnDate(new Date().toISOString().split('T')[0])
    setRemarks('')
  }

  const getStatusBadge = (status: string) => {
    const colors = {
      draft: 'bg-gray-100 text-gray-800',
      pending_review: 'bg-blue-100 text-blue-800',
      approved: 'bg-green-100 text-green-800',
      submitted: 'bg-purple-100 text-purple-800',
      rejected: 'bg-red-100 text-red-800',
    }
    return (
      <Badge className={colors[status as keyof typeof colors] || 'bg-gray-100 text-gray-800'}>
        {status.replace('_', ' ').toUpperCase()}
      </Badge>
    )
  }

  const openGenerateDialog = (type: 'crilc' | 'sma') => {
    setReportType(type)
    setGenerateDialogOpen(true)
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Quarterly Reports</h1>
          <p className="text-muted-foreground">
            Generate and manage CRILC & SMA quarterly regulatory returns
          </p>
        </div>
      </div>

      {/* Tabs */}
      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList>
          <TabsTrigger value="crilc">CRILC Returns</TabsTrigger>
          <TabsTrigger value="sma">SMA Reports</TabsTrigger>
        </TabsList>

        {/* CRILC Returns Tab */}
        <TabsContent value="crilc" className="space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-xl font-semibold">CRILC Quarterly Returns</h2>
              <p className="text-sm text-muted-foreground">
                Large credit reporting for RBI
              </p>
            </div>
            <Button onClick={() => openGenerateDialog('crilc')}>
              <Plus className="h-4 w-4 mr-2" />
              Generate New Return
            </Button>
          </div>

          <Card>
            <CardHeader>
              <CardTitle>CRILC Returns History</CardTitle>
            </CardHeader>
            <CardContent>
              {crilcLoading ? (
                <QuarterlyReportsSkeleton />
              ) : (
                <>
                  <Table>
                    <TableHeader>
                      <TableRow>
                        <TableHead>Return Number</TableHead>
                        <TableHead>Quarter</TableHead>
                        <TableHead>As On Date</TableHead>
                        <TableHead>Borrowers</TableHead>
                        <TableHead className="text-right">Total Exposure</TableHead>
                        <TableHead>Status</TableHead>
                        <TableHead className="text-right">Actions</TableHead>
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      {crilcReturns?.data?.items?.length === 0 ? (
                        <TableRow>
                          <TableCell colSpan={7} className="text-center text-muted-foreground">
                            No CRILC returns found. Generate your first return to get started.
                          </TableCell>
                        </TableRow>
                      ) : (
                        crilcReturns?.data?.items?.map((returnItem: CRILCQuarterlyReturn) => (
                          <TableRow key={returnItem.id}>
                            <TableCell className="font-medium">
                              {returnItem.return_number}
                            </TableCell>
                            <TableCell>
                              <div>
                                <div className="font-medium">{returnItem.reporting_quarter}</div>
                                <div className="text-xs text-muted-foreground">
                                  {returnItem.reporting_year}
                                </div>
                              </div>
                            </TableCell>
                            <TableCell>
                              <div className="flex items-center gap-2">
                                <Calendar className="h-4 w-4 text-muted-foreground" />
                                {formatDate(returnItem.as_on_date)}
                              </div>
                            </TableCell>
                            <TableCell>{returnItem.total_large_borrowers}</TableCell>
                            <TableCell className="text-right">
                              {formatCurrency(returnItem.total_exposure)}
                            </TableCell>
                            <TableCell>{getStatusBadge(returnItem.status)}</TableCell>
                            <TableCell className="text-right">
                              <div className="flex items-center justify-end gap-2">
                                {returnItem.status === 'draft' && (
                                  <Button
                                    size="sm"
                                    variant="outline"
                                    onClick={() => handleApprove(returnItem.id)}
                                  >
                                    <CheckCircle className="h-4 w-4 mr-1" />
                                    Approve
                                  </Button>
                                )}
                                {returnItem.status === 'approved' && (
                                  <Button
                                    size="sm"
                                    onClick={() => handleSubmit(returnItem.id)}
                                  >
                                    <Send className="h-4 w-4 mr-1" />
                                    Submit
                                  </Button>
                                )}
                                <Button size="sm" variant="ghost">
                                  <Eye className="h-4 w-4" />
                                </Button>
                              </div>
                            </TableCell>
                          </TableRow>
                        ))
                      )}
                    </TableBody>
                  </Table>

                  {/* Summary Stats */}
                  {crilcReturns?.data?.items && crilcReturns.data.items.length > 0 && (
                    <div className="mt-6 grid gap-4 md:grid-cols-3">
                      <Card className="bg-blue-50">
                        <CardHeader className="pb-2">
                          <CardTitle className="text-sm">Total Returns</CardTitle>
                        </CardHeader>
                        <CardContent>
                          <div className="text-2xl font-bold">{crilcReturns.total}</div>
                        </CardContent>
                      </Card>

                      <Card className="bg-green-50">
                        <CardHeader className="pb-2">
                          <CardTitle className="text-sm">Submitted</CardTitle>
                        </CardHeader>
                        <CardContent>
                          <div className="text-2xl font-bold text-green-600">
                            {crilcReturns.items.filter((r: CRILCQuarterlyReturn) => r.status === 'submitted').length}
                          </div>
                        </CardContent>
                      </Card>

                      <Card className="bg-yellow-50">
                        <CardHeader className="pb-2">
                          <CardTitle className="text-sm">Pending</CardTitle>
                        </CardHeader>
                        <CardContent>
                          <div className="text-2xl font-bold text-yellow-600">
                            {crilcReturns.items.filter((r: CRILCQuarterlyReturn) =>
                              ['draft', 'pending_review', 'approved'].includes(r.status)
                            ).length}
                          </div>
                        </CardContent>
                      </Card>
                    </div>
                  )}
                </>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* SMA Reports Tab */}
        <TabsContent value="sma" className="space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-xl font-semibold">SMA Quarterly Reports</h2>
              <p className="text-sm text-muted-foreground">
                Special Mention Account movement reporting
              </p>
            </div>
            <Button onClick={() => openGenerateDialog('sma')}>
              <Plus className="h-4 w-4 mr-2" />
              Generate New Report
            </Button>
          </div>

          <Card>
            <CardContent className="pt-6">
              <div className="text-center text-muted-foreground py-8">
                SMA quarterly reports will be displayed here
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>

      {/* Generate Dialog */}
      <Dialog open={generateDialogOpen} onOpenChange={setGenerateDialogOpen}>
        <DialogContent className="max-w-md">
          <DialogHeader>
            <DialogTitle>
              Generate {reportType === 'crilc' ? 'CRILC Return' : 'SMA Report'}
            </DialogTitle>
            <DialogDescription>
              Enter details for the quarterly {reportType === 'crilc' ? 'return' : 'report'}
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <Label htmlFor="quarter">Reporting Quarter</Label>
                <Input
                  id="quarter"
                  value={quarter}
                  onChange={(e) => setQuarter(e.target.value)}
                  placeholder="Q1FY25"
                />
              </div>
              <div>
                <Label htmlFor="year">Reporting Year</Label>
                <Input
                  id="year"
                  value={year}
                  onChange={(e) => setYear(e.target.value)}
                  placeholder="FY2024-25"
                />
              </div>
            </div>
            <div>
              <Label htmlFor="as-on-date">As On Date</Label>
              <Input
                id="as-on-date"
                type="date"
                value={asOnDate}
                onChange={(e) => setAsOnDate(e.target.value)}
              />
            </div>
            <div>
              <Label htmlFor="remarks">Remarks (Optional)</Label>
              <Input
                id="remarks"
                value={remarks}
                onChange={(e) => setRemarks(e.target.value)}
                placeholder="Any additional notes..."
              />
            </div>
            <div className="rounded-lg bg-blue-50 p-4">
              <p className="text-sm text-blue-900">
                This will generate a {reportType === 'crilc' ? 'CRILC return' : 'SMA report'} with
                all relevant data for the specified period. Review before submission to RBI.
              </p>
            </div>
          </div>
          <DialogFooter>
            <Button
              variant="outline"
              onClick={() => {
                setGenerateDialogOpen(false)
                resetForm()
              }}
            >
              Cancel
            </Button>
            <Button
              onClick={handleGenerate}
              disabled={
                generateCRILCMutation.isPending ||
                generateSMAMutation.isPending ||
                !quarter ||
                !year ||
                !asOnDate
              }
            >
              {(generateCRILCMutation.isPending || generateSMAMutation.isPending)
                ? 'Generating...'
                : 'Generate'}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  )
}

function QuarterlyReportsSkeleton() {
  return (
    <div className="space-y-4">
      {[...Array(3)].map((_, i) => (
        <Skeleton key={i} className="h-16 w-full" />
      ))}
    </div>
  )
}
