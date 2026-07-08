'use client'

import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useParams, useRouter } from 'next/navigation'
import { 
  Download, 
  Printer, 
  Book,
  ArrowLeft,
  Calendar,
  FileText,
  CheckCircle,
  RefreshCw
} from 'lucide-react'
import { DashboardLayout } from '@/components/layout/dashboard-layout'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
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
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { Skeleton } from '@/components/ui/skeleton'
import { depositService } from '@/services/deposit.service'
import { formatCurrency, formatDate } from '@/lib/utils'
import { useToast } from '@/hooks/use-toast'

export default function PassbookPage() {
  const params = useParams()
  const router = useRouter()
  const { toast } = useToast()
  const queryClient = useQueryClient()
  const accountId = parseInt(params.accountId as string)

  const [page, setPage] = useState(1)
  const [selectedEntries, setSelectedEntries] = useState<number[]>([])
  const [pageSize, setPageSize] = useState(20)

  // Fetch account details
  const { data: accountData, isLoading: accountLoading } = useQuery({
    queryKey: ['deposit-account', accountId],
    queryFn: () => depositService.getAccount(accountId.toString()),
  })

  // Fetch passbook entries
  const { data: entriesData, isLoading: entriesLoading, refetch } = useQuery({
    queryKey: ['passbook-entries', accountId, page, pageSize],
    queryFn: () => depositService.getPassbookEntries(accountId, { page, page_size: pageSize }),
  })

  // Fetch passbook summary
  const { data: summaryData, isLoading: summaryLoading } = useQuery({
    queryKey: ['passbook-summary', accountId],
    queryFn: () => depositService.getPassbookSummary(accountId),
  })

  // Download PDF mutation
  const downloadPDFMutation = useMutation({
    mutationFn: () => depositService.generatePassbookPDF(accountId),
    onSuccess: (response) => {
      const blob = response.data
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `passbook_${accountData?.data?.account_number}_${new Date().toISOString().split('T')[0]}.pdf`
      document.body.appendChild(a)
      a.click()
      document.body.removeChild(a)
      window.URL.revokeObjectURL(url)
      
      toast({
        title: 'Success',
        description: 'Passbook PDF downloaded successfully',
      })
    },
    onError: () => {
      toast({
        title: 'Error',
        description: 'Failed to generate passbook PDF',
        variant: 'destructive',
      })
    },
  })

  // Mark entries as printed mutation
  const markPrintedMutation = useMutation({
    mutationFn: (data: { entry_ids: number[]; page_number: number }) =>
      depositService.markPassbookPrinted(accountId, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['passbook-entries', accountId] })
      queryClient.invalidateQueries({ queryKey: ['passbook-summary', accountId] })
      setSelectedEntries([])
      toast({
        title: 'Success',
        description: 'Entries marked as printed',
      })
    },
    onError: () => {
      toast({
        title: 'Error',
        description: 'Failed to mark entries as printed',
        variant: 'destructive',
      })
    },
  })

  // Issue new passbook mutation
  const issuePassbookMutation = useMutation({
    mutationFn: () => depositService.issuePassbook(accountId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['passbook-summary', accountId] })
      queryClient.invalidateQueries({ queryKey: ['deposit-account', accountId] })
      toast({
        title: 'Success',
        description: 'New passbook issued successfully',
      })
    },
    onError: () => {
      toast({
        title: 'Error',
        description: 'Failed to issue new passbook',
        variant: 'destructive',
      })
    },
  })

  const handleDownloadPDF = () => {
    downloadPDFMutation.mutate()
  }

  const handleMarkPrinted = () => {
    if (selectedEntries.length === 0) {
      toast({
        title: 'Warning',
        description: 'Please select entries to mark as printed',
        variant: 'destructive',
      })
      return
    }

    const currentPage = summaryData?.data?.current_page_number || 1
    markPrintedMutation.mutate({
      entry_ids: selectedEntries,
      page_number: currentPage,
    })
  }

  const handleIssuePassbook = () => {
    issuePassbookMutation.mutate()
  }

  const toggleEntrySelection = (entryId: number) => {
    setSelectedEntries((prev) =>
      prev.includes(entryId)
        ? prev.filter((id) => id !== entryId)
        : [...prev, entryId]
    )
  }

  const toggleSelectAll = () => {
    if (selectedEntries.length === entriesData?.data?.items?.length) {
      setSelectedEntries([])
    } else {
      setSelectedEntries(entriesData?.data?.items?.map((entry: any) => entry.id) || [])
    }
  }

  return (
    <DashboardLayout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <Button variant="ghost" onClick={() => router.back()}>
              <ArrowLeft className="h-4 w-4 mr-2" />
              Back
            </Button>
            <div>
              <h1 className="text-3xl font-bold text-gray-900">Passbook</h1>
              {accountData && (
                <p className="text-gray-600 mt-1">
                  Account: {accountData.data?.account_number} - {accountData.data?.customer_name}
                </p>
              )}
            </div>
          </div>
          <div className="flex gap-2">
            <Button
              variant="outline"
              onClick={handleDownloadPDF}
              disabled={downloadPDFMutation.isPending}
            >
              {downloadPDFMutation.isPending ? (
                <RefreshCw className="h-4 w-4 mr-2 animate-spin" />
              ) : (
                <Download className="h-4 w-4 mr-2" />
              )}
              Download PDF
            </Button>
            <Button
              variant="outline"
              onClick={handleMarkPrinted}
              disabled={markPrintedMutation.isPending || selectedEntries.length === 0}
            >
              <Printer className="h-4 w-4 mr-2" />
              Mark as Printed
            </Button>
            <Button
              onClick={handleIssuePassbook}
              disabled={issuePassbookMutation.isPending}
            >
              <Book className="h-4 w-4 mr-2" />
              Issue New Passbook
            </Button>
          </div>
        </div>

        {/* Summary Cards */}
        {summaryLoading ? (
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
            {[1, 2, 3, 4].map((i) => (
              <Card key={i}>
                <CardContent className="pt-6">
                  <Skeleton className="h-20 w-full" />
                </CardContent>
              </Card>
            ))}
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-medium text-gray-600">
                  Total Entries
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">
                  {summaryData?.data?.total_entries || 0}
                </div>
                <p className="text-xs text-gray-600 mt-1">
                  All transactions
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-medium text-gray-600">
                  Unprinted Entries
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-orange-600">
                  {summaryData?.data?.unprinted_entries || 0}
                </div>
                <p className="text-xs text-gray-600 mt-1">
                  Pending printing
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-medium text-gray-600">
                  Current Page
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">
                  {summaryData?.data?.current_page_number || 1}
                </div>
                <p className="text-xs text-gray-600 mt-1">
                  Page number
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-medium text-gray-600">
                  Current Balance
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-green-600">
                  {formatCurrency(accountData?.data?.current_balance || 0)}
                </div>
                <p className="text-xs text-gray-600 mt-1">
                  As of today
                </p>
              </CardContent>
            </Card>
          </div>
        )}

        {/* Passbook Entries Table */}
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <CardTitle>Passbook Entries</CardTitle>
              <div className="flex items-center gap-2">
                <span className="text-sm text-gray-600">Entries per page:</span>
                <Select
                  value={pageSize.toString()}
                  onValueChange={(value) => {
                    setPageSize(parseInt(value))
                    setPage(1)
                  }}
                >
                  <SelectTrigger className="w-20">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="10">10</SelectItem>
                    <SelectItem value="20">20</SelectItem>
                    <SelectItem value="50">50</SelectItem>
                    <SelectItem value="100">100</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>
          </CardHeader>
          <CardContent>
            {entriesLoading ? (
              <div className="space-y-2">
                {[1, 2, 3, 4, 5].map((i) => (
                  <Skeleton key={i} className="h-12 w-full" />
                ))}
              </div>
            ) : (
              <div className="overflow-x-auto">
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead className="w-12">
                        <input
                          type="checkbox"
                          checked={
                            selectedEntries.length === entriesData?.data?.items?.length &&
                            entriesData?.data?.items?.length > 0
                          }
                          onChange={toggleSelectAll}
                          className="rounded border-gray-300"
                        />
                      </TableHead>
                      <TableHead>Date</TableHead>
                      <TableHead>Particulars</TableHead>
                      <TableHead className="text-right">Withdrawal</TableHead>
                      <TableHead className="text-right">Deposit</TableHead>
                      <TableHead className="text-right">Balance</TableHead>
                      <TableHead>Page</TableHead>
                      <TableHead>Status</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {entriesData?.data?.items?.map((entry: any) => (
                      <TableRow key={entry.id}>
                        <TableCell>
                          <input
                            type="checkbox"
                            checked={selectedEntries.includes(entry.id)}
                            onChange={() => toggleEntrySelection(entry.id)}
                            className="rounded border-gray-300"
                          />
                        </TableCell>
                        <TableCell>{formatDate(entry.entry_date)}</TableCell>
                        <TableCell className="max-w-md">
                          <div className="truncate" title={entry.particulars}>
                            {entry.particulars}
                          </div>
                        </TableCell>
                        <TableCell className="text-right text-red-600">
                          {entry.withdrawal_amount > 0 && formatCurrency(entry.withdrawal_amount)}
                        </TableCell>
                        <TableCell className="text-right text-green-600">
                          {entry.deposit_amount > 0 && formatCurrency(entry.deposit_amount)}
                        </TableCell>
                        <TableCell className="text-right font-semibold">
                          {formatCurrency(entry.balance)}
                        </TableCell>
                        <TableCell>
                          {entry.page_number ? (
                            <Badge variant="outline">Page {entry.page_number}</Badge>
                          ) : (
                            <span className="text-gray-400">-</span>
                          )}
                        </TableCell>
                        <TableCell>
                          {entry.printed ? (
                            <Badge className="bg-green-100 text-green-800">
                              <CheckCircle className="h-3 w-3 mr-1" />
                              Printed
                            </Badge>
                          ) : (
                            <Badge variant="secondary">Pending</Badge>
                          )}
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>

                {(!entriesData?.data?.items || entriesData.data.items.length === 0) && (
                  <div className="text-center py-12 text-gray-500">
                    <FileText className="h-16 w-16 mx-auto mb-4 opacity-50" />
                    <p className="text-lg font-medium">No passbook entries found</p>
                    <p className="text-sm mt-1">Transactions will appear here once posted</p>
                  </div>
                )}
              </div>
            )}

            {/* Pagination */}
            {entriesData?.data?.total > 0 && (
              <div className="flex items-center justify-between mt-6">
                <p className="text-sm text-gray-600">
                  Showing {((page - 1) * pageSize) + 1} to{' '}
                  {Math.min(page * pageSize, entriesData?.data?.total || 0)} of{' '}
                  {entriesData?.data?.total || 0} entries
                </p>
                <div className="flex gap-2">
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => setPage((p) => Math.max(1, p - 1))}
                    disabled={page === 1}
                  >
                    Previous
                  </Button>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => setPage((p) => p + 1)}
                    disabled={page * pageSize >= (entriesData?.data?.total || 0)}
                  >
                    Next
                  </Button>
                </div>
              </div>
            )}
          </CardContent>
        </Card>

        {/* Info Card */}
        <Card className="bg-blue-50 border-blue-200">
          <CardContent className="pt-6">
            <div className="flex gap-3">
              <FileText className="h-5 w-5 text-blue-600 mt-0.5" />
              <div>
                <h3 className="font-semibold text-blue-900">Passbook Information</h3>
                <ul className="text-sm text-blue-800 mt-2 space-y-1 list-disc list-inside">
                  <li>Select entries and click "Mark as Printed" after physical printing</li>
                  <li>Download PDF to generate a digital passbook for the customer</li>
                  <li>Issue new passbook when the current one is full or damaged</li>
                  <li>All transactions are automatically recorded in the passbook</li>
                </ul>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </DashboardLayout>
  )
}
