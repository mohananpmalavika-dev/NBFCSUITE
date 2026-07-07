'use client'

/**
 * CRILC Large Credits Page
 * List and manage large credit borrowers (≥₹5 Crore)
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
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
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
import { Plus, Search, RefreshCw, TrendingUp, AlertCircle, Eye } from 'lucide-react'
import { complianceService } from '@/services/compliance.service'
import { formatCurrency, formatDate } from '@/lib/utils'
import type { CRILCBorrower, LargeCreditIdentificationRequest } from '@/types/compliance.types'
import { toast } from '@/components/ui/use-toast'
import { Skeleton } from '@/components/ui/skeleton'
import Link from 'next/link'

export default function LargeCreditsPage() {
  const queryClient = useQueryClient()
  const [searchQuery, setSearchQuery] = useState('')
  const [smaFilter, setSmaFilter] = useState<string>('all')
  const [page, setPage] = useState(1)
  const [identifyDialogOpen, setIdentifyDialogOpen] = useState(false)
  const [identifyDate, setIdentifyDate] = useState(
    new Date().toISOString().split('T')[0]
  )
  const [thresholdAmount, setThresholdAmount] = useState('50000000')

  const { data, isLoading, refetch } = useQuery({
    queryKey: ['large-credits', page, smaFilter],
    queryFn: () =>
      complianceService.getBorrowers({
        skip: (page - 1) * 20,
        limit: 20,
        is_large_credit: true,
        sma_status: smaFilter !== 'all' ? smaFilter : undefined,
      }),
  })

  const identifyMutation = useMutation({
    mutationFn: (data: LargeCreditIdentificationRequest) =>
      complianceService.identifyLargeCredits(data),
    onSuccess: (result) => {
      toast({
        title: 'Large Credits Identified',
        description: `Found ${result.data.total_large_credits} large credits. ${result.data.newly_identified} newly identified.`,
      })
      setIdentifyDialogOpen(false)
      queryClient.invalidateQueries({ queryKey: ['large-credits'] })
    },
    onError: () => {
      toast({
        title: 'Error',
        description: 'Failed to identify large credits',
        variant: 'destructive',
      })
    },
  })

  const handleIdentify = () => {
    identifyMutation.mutate({
      threshold_amount: parseFloat(thresholdAmount),
      as_on_date: identifyDate,
      include_group_exposure: true,
    })
  }

  const getSMABadge = (status: string) => {
    const colors = {
      standard: 'bg-green-100 text-green-800',
      sma_0: 'bg-yellow-100 text-yellow-800',
      sma_1: 'bg-orange-100 text-orange-800',
      sma_2: 'bg-red-100 text-red-800',
      npa_substandard: 'bg-red-200 text-red-900',
    }
    const labels = {
      standard: 'Standard',
      sma_0: 'SMA-0',
      sma_1: 'SMA-1',
      sma_2: 'SMA-2',
      npa_substandard: 'NPA',
    }
    return (
      <Badge className={colors[status as keyof typeof colors] || 'bg-gray-100 text-gray-800'}>
        {labels[status as keyof typeof labels] || status}
      </Badge>
    )
  }

  const filteredBorrowers = data?.data?.items?.filter((borrower: CRILCBorrower) =>
    borrower.borrower_name.toLowerCase().includes(searchQuery.toLowerCase()) ||
    borrower.borrower_code.toLowerCase().includes(searchQuery.toLowerCase()) ||
    borrower.pan_number?.toLowerCase().includes(searchQuery.toLowerCase())
  ) || []

  if (isLoading) {
    return <LargeCreditsSkeleton />
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">CRILC Large Credits</h1>
          <p className="text-muted-foreground">
            Borrowers with aggregate exposure ≥ ₹5 Crore
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Dialog open={identifyDialogOpen} onOpenChange={setIdentifyDialogOpen}>
            <DialogTrigger asChild>
              <Button>
                <RefreshCw className="h-4 w-4 mr-2" />
                Identify Large Credits
              </Button>
            </DialogTrigger>
            <DialogContent>
              <DialogHeader>
                <DialogTitle>Identify Large Credits</DialogTitle>
                <DialogDescription>
                  Run identification process to find borrowers meeting large credit threshold
                </DialogDescription>
              </DialogHeader>
              <div className="space-y-4">
                <div>
                  <Label htmlFor="threshold">Threshold Amount (₹)</Label>
                  <Input
                    id="threshold"
                    type="number"
                    value={thresholdAmount}
                    onChange={(e) => setThresholdAmount(e.target.value)}
                    placeholder="50000000"
                  />
                  <p className="text-xs text-muted-foreground mt-1">
                    Default: ₹5 Crore (50,000,000)
                  </p>
                </div>
                <div>
                  <Label htmlFor="date">As On Date</Label>
                  <Input
                    id="date"
                    type="date"
                    value={identifyDate}
                    onChange={(e) => setIdentifyDate(e.target.value)}
                  />
                </div>
              </div>
              <DialogFooter>
                <Button
                  onClick={handleIdentify}
                  disabled={identifyMutation.isPending}
                >
                  {identifyMutation.isPending ? 'Identifying...' : 'Identify'}
                </Button>
              </DialogFooter>
            </DialogContent>
          </Dialog>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="grid gap-4 md:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Large Credits</CardTitle>
            <TrendingUp className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{data?.data?.total || 0}</div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Exposure</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {formatCurrency(
                data?.data?.items?.reduce((sum: number, b: CRILCBorrower) => sum + b.total_credit_exposure, 0) || 0
              )}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">SMA Accounts</CardTitle>
            <AlertCircle className="h-4 w-4 text-orange-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-orange-600">
              {data?.data?.items?.filter((b: CRILCBorrower) =>
                ['sma_0', 'sma_1', 'sma_2'].includes(b.current_sma_status)
              ).length || 0}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">NPA Accounts</CardTitle>
            <AlertCircle className="h-4 w-4 text-red-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-red-600">
              {data?.data?.items?.filter((b: CRILCBorrower) =>
                b.current_sma_status.startsWith('npa')
              ).length || 0}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Filters and Search */}
      <Card>
        <CardContent className="pt-6">
          <div className="flex items-center gap-4">
            <div className="flex-1 relative">
              <Search className="absolute left-2 top-2.5 h-4 w-4 text-muted-foreground" />
              <Input
                placeholder="Search by name, code, or PAN..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="pl-8"
              />
            </div>
            <Select value={smaFilter} onValueChange={setSmaFilter}>
              <SelectTrigger className="w-48">
                <SelectValue placeholder="Filter by SMA" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Status</SelectItem>
                <SelectItem value="standard">Standard</SelectItem>
                <SelectItem value="sma_0">SMA-0</SelectItem>
                <SelectItem value="sma_1">SMA-1</SelectItem>
                <SelectItem value="sma_2">SMA-2</SelectItem>
                <SelectItem value="npa_substandard">NPA</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </CardContent>
      </Card>

      {/* Borrowers Table */}
      <Card>
        <CardHeader>
          <CardTitle>Large Credit Borrowers</CardTitle>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Borrower Code</TableHead>
                <TableHead>Borrower Name</TableHead>
                <TableHead>PAN</TableHead>
                <TableHead>Industry</TableHead>
                <TableHead className="text-right">Total Exposure</TableHead>
                <TableHead>SMA Status</TableHead>
                <TableHead className="text-center">DPD</TableHead>
                <TableHead className="text-right">Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {filteredBorrowers.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={8} className="text-center text-muted-foreground">
                    No large credit borrowers found
                  </TableCell>
                </TableRow>
              ) : (
                filteredBorrowers.map((borrower: CRILCBorrower) => (
                  <TableRow key={borrower.id}>
                    <TableCell className="font-medium">{borrower.borrower_code}</TableCell>
                    <TableCell>
                      <div>
                        <div className="font-medium">{borrower.borrower_name}</div>
                        <div className="text-xs text-muted-foreground">
                          {borrower.borrower_type}
                        </div>
                      </div>
                    </TableCell>
                    <TableCell>{borrower.pan_number || '-'}</TableCell>
                    <TableCell>
                      <div className="text-sm">{borrower.industry_name || '-'}</div>
                    </TableCell>
                    <TableCell className="text-right font-medium">
                      {formatCurrency(borrower.total_credit_exposure)}
                    </TableCell>
                    <TableCell>{getSMABadge(borrower.current_sma_status)}</TableCell>
                    <TableCell className="text-center">
                      <Badge variant={borrower.days_past_due > 0 ? 'destructive' : 'secondary'}>
                        {borrower.days_past_due} days
                      </Badge>
                    </TableCell>
                    <TableCell className="text-right">
                      <Link href={`/compliance/large-credits/${borrower.id}`}>
                        <Button variant="ghost" size="sm">
                          <Eye className="h-4 w-4" />
                        </Button>
                      </Link>
                    </TableCell>
                  </TableRow>
                ))
              )}
            </TableBody>
          </Table>

          {/* Pagination */}
          {data && data.data && data.data.total > 20 && (
            <div className="flex items-center justify-between mt-4">
              <div className="text-sm text-muted-foreground">
                Showing {(page - 1) * 20 + 1} to {Math.min(page * 20, data.data.total)} of {data.data.total} borrowers
              </div>
              <div className="flex items-center gap-2">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => setPage(page - 1)}
                  disabled={page === 1}
                >
                  Previous
                </Button>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => setPage(page + 1)}
                  disabled={page * 20 >= data.data.total}
                >
                  Next
                </Button>
              </div>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  )
}

function LargeCreditsSkeleton() {
  return (
    <div className="space-y-6">
      <Skeleton className="h-12 w-96" />
      <div className="grid gap-4 md:grid-cols-4">
        {[...Array(4)].map((_, i) => (
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
        <CardContent className="pt-6">
          <Skeleton className="h-10 w-full" />
        </CardContent>
      </Card>
      <Card>
        <CardHeader>
          <Skeleton className="h-6 w-48" />
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {[...Array(5)].map((_, i) => (
              <Skeleton key={i} className="h-16 w-full" />
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
