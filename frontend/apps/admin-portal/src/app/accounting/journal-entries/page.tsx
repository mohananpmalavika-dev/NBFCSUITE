'use client'

import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import Link from 'next/link'
import { Plus, Search, Filter, Eye, MoreVertical, FileText, CheckCircle, XCircle } from 'lucide-react'
import { DashboardLayout } from '@/components/layout/dashboard-layout'
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
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu'
import { Skeleton } from '@/components/ui/skeleton'
import { Card, CardContent } from '@/components/ui/card'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { accountingService } from '@/services/accounting.service'
import { formatCurrency, formatDate, getStatusColor } from '@/lib/utils'
import { useToast } from '@/hooks/use-toast'
import type { JournalEntry } from '@/types'

export default function JournalEntriesPage() {
  const [page, setPage] = useState(1)
  const [search, setSearch] = useState('')
  const [statusFilter, setStatusFilter] = useState<string>('')
  const [typeFilter, setTypeFilter] = useState<string>('')

  const queryClient = useQueryClient()
  const { toast } = useToast()

  const { data, isLoading } = useQuery({
    queryKey: ['journal-entries', page, search, statusFilter, typeFilter],
    queryFn: () => accountingService.getJournalEntries({ 
      page, 
      page_size: 20,
      status: statusFilter || undefined,
      entry_type: typeFilter || undefined
    }),
  })

  const postMutation = useMutation({
    mutationFn: (entryId: string) => accountingService.postJournalEntry(entryId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['journal-entries'] })
      toast({
        title: 'Entry posted',
        description: 'Journal entry has been posted to general ledger',
      })
    },
    onError: () => {
      toast({
        title: 'Error',
        description: 'Failed to post journal entry',
        variant: 'destructive',
      })
    },
  })

  const handlePost = (entryId: string) => {
    postMutation.mutate(entryId)
  }

  // Calculate stats
  const stats = data?.data?.items?.reduce(
    (acc, entry: JournalEntry) => {
      if (entry.entry_status === 'draft') acc.draft++
      else if (entry.entry_status === 'posted') acc.posted++
      else if (entry.entry_status === 'reversed') acc.reversed++
      
      acc.totalDebit += entry.total_debit
      acc.totalCredit += entry.total_credit
      
      return acc
    },
    { draft: 0, posted: 0, reversed: 0, totalDebit: 0, totalCredit: 0 }
  ) || { draft: 0, posted: 0, reversed: 0, totalDebit: 0, totalCredit: 0 }

  return (
    <DashboardLayout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Journal Entries</h1>
            <p className="text-gray-600 mt-1">Record and manage accounting journal entries</p>
          </div>
          <Button>
            <Plus className="h-4 w-4 mr-2" />
            New Entry
          </Button>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
          <StatCard
            label="Draft"
            value={stats.draft}
            icon={FileText}
            color="blue"
          />
          <StatCard
            label="Posted"
            value={stats.posted}
            icon={CheckCircle}
            color="green"
          />
          <StatCard
            label="Reversed"
            value={stats.reversed}
            icon={XCircle}
            color="red"
          />
          <StatCard
            label="Total Debit"
            value={formatCurrency(stats.totalDebit)}
            icon={FileText}
            color="purple"
            isAmount
          />
          <StatCard
            label="Total Credit"
            value={formatCurrency(stats.totalCredit)}
            icon={FileText}
            color="orange"
            isAmount
          />
        </div>

        {/* Filters */}
        <div className="flex items-center gap-4">
          <div className="flex-1 relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
            <Input
              type="search"
              placeholder="Search by entry number, narration..."
              className="pl-10"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
            />
          </div>
          <select
            value={typeFilter}
            onChange={(e) => setTypeFilter(e.target.value)}
            className="flex h-10 rounded-md border border-input bg-background px-3 py-2 text-sm"
          >
            <option value="">All Types</option>
            <option value="Manual">Manual</option>
            <option value="System">System</option>
          </select>
          <Button variant="outline">
            <Filter className="h-4 w-4 mr-2" />
            More Filters
          </Button>
        </div>

        {/* Entries Tabs */}
        <Tabs value={statusFilter} onValueChange={setStatusFilter}>
          <TabsList>
            <TabsTrigger value="">All Entries</TabsTrigger>
            <TabsTrigger value="draft">Draft</TabsTrigger>
            <TabsTrigger value="posted">Posted</TabsTrigger>
            <TabsTrigger value="reversed">Reversed</TabsTrigger>
          </TabsList>

          <TabsContent value={statusFilter} className="space-y-4">
            {/* Table */}
            <div className="bg-white rounded-lg border">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Entry Number</TableHead>
                    <TableHead>Entry Date</TableHead>
                    <TableHead>Narration</TableHead>
                    <TableHead>Type</TableHead>
                    <TableHead>Debit</TableHead>
                    <TableHead>Credit</TableHead>
                    <TableHead>Status</TableHead>
                    <TableHead className="text-right">Actions</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {isLoading ? (
                    [...Array(5)].map((_, i) => (
                      <TableRow key={i}>
                        <TableCell><Skeleton className="h-4 w-28" /></TableCell>
                        <TableCell><Skeleton className="h-4 w-24" /></TableCell>
                        <TableCell><Skeleton className="h-4 w-48" /></TableCell>
                        <TableCell><Skeleton className="h-5 w-16" /></TableCell>
                        <TableCell><Skeleton className="h-4 w-24" /></TableCell>
                        <TableCell><Skeleton className="h-4 w-24" /></TableCell>
                        <TableCell><Skeleton className="h-5 w-20" /></TableCell>
                        <TableCell><Skeleton className="h-8 w-8 ml-auto" /></TableCell>
                      </TableRow>
                    ))
                  ) : data?.data?.items && data.data.items.length > 0 ? (
                    data.data.items.map((entry: JournalEntry) => (
                      <TableRow key={entry.id}>
                        <TableCell className="font-mono text-sm font-medium">
                          {entry.entry_number}
                        </TableCell>
                        <TableCell className="text-sm text-gray-600">
                          {formatDate(entry.entry_date)}
                        </TableCell>
                        <TableCell>
                          <p className="line-clamp-2">{entry.description}</p>
                        </TableCell>
                        <TableCell>
                          <Badge variant="outline">{entry.entry_type}</Badge>
                        </TableCell>
                        <TableCell className="font-semibold">
                          {formatCurrency(entry.total_debit)}
                        </TableCell>
                        <TableCell className="font-semibold">
                          {formatCurrency(entry.total_credit)}
                        </TableCell>
                        <TableCell>
                          <Badge className={getStatusColor(entry.entry_status)}>
                            {entry.entry_status}
                          </Badge>
                        </TableCell>
                        <TableCell className="text-right">
                          <DropdownMenu>
                            <DropdownMenuTrigger asChild>
                              <Button variant="ghost" size="icon">
                                <MoreVertical className="h-4 w-4" />
                              </Button>
                            </DropdownMenuTrigger>
                            <DropdownMenuContent align="end">
                              <DropdownMenuItem>
                                <Eye className="h-4 w-4 mr-2" />
                                View Details
                              </DropdownMenuItem>
                              {entry.entry_status === 'draft' && (
                                <DropdownMenuItem 
                                  onClick={() => handlePost(entry.id)}
                                  disabled={postMutation.isPending}
                                >
                                  <CheckCircle className="h-4 w-4 mr-2" />
                                  Post Entry
                                </DropdownMenuItem>
                              )}
                              {entry.entry_status === 'posted' && (
                                <DropdownMenuItem className="text-red-600">
                                  <XCircle className="h-4 w-4 mr-2" />
                                  Reverse Entry
                                </DropdownMenuItem>
                              )}
                            </DropdownMenuContent>
                          </DropdownMenu>
                        </TableCell>
                      </TableRow>
                    ))
                  ) : (
                    <TableRow>
                      <TableCell colSpan={8} className="text-center py-8 text-gray-500">
                        <FileText className="h-12 w-12 mx-auto text-gray-400 mb-2" />
                        <p>No journal entries found</p>
                        <Button variant="link" className="mt-2">
                          Create your first entry
                        </Button>
                      </TableCell>
                    </TableRow>
                  )}
                </TableBody>
              </Table>

              {/* Pagination */}
              {data?.data && data.data.items.length > 0 && (
                <div className="flex items-center justify-between px-6 py-4 border-t">
                  <p className="text-sm text-gray-600">
                    Showing {((page - 1) * 20) + 1} to {Math.min(page * 20, data.data?.total || 0)} of {data.data?.total || 0} entries
                  </p>
                  <div className="flex gap-2">
                    <Button
                      variant="outline"
                      size="sm"
                      disabled={!data.data?.has_prev}
                      onClick={() => setPage(page - 1)}
                    >
                      Previous
                    </Button>
                    <Button
                      variant="outline"
                      size="sm"
                      disabled={!data.data?.has_next}
                      onClick={() => setPage(page + 1)}
                    >
                      Next
                    </Button>
                  </div>
                </div>
              )}
            </div>
          </TabsContent>
        </Tabs>
      </div>
    </DashboardLayout>
  )
}

function StatCard({ 
  label, 
  value, 
  icon: Icon,
  color = 'blue',
  isAmount = false
}: { 
  label: string
  value: number | string
  icon: any
  color?: 'blue' | 'green' | 'yellow' | 'red' | 'purple' | 'orange'
  isAmount?: boolean
}) {
  const colors = {
    blue: 'bg-blue-100 text-blue-600',
    green: 'bg-green-100 text-green-600',
    yellow: 'bg-yellow-100 text-yellow-600',
    red: 'bg-red-100 text-red-600',
    purple: 'bg-purple-100 text-purple-600',
    orange: 'bg-orange-100 text-orange-600',
  }

  return (
    <Card>
      <CardContent className="pt-6">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-sm text-gray-600 mb-1">{label}</p>
            <p className={`${isAmount ? 'text-xl' : 'text-2xl'} font-bold text-gray-900`}>
              {value}
            </p>
          </div>
          <div className={`h-12 w-12 rounded-lg ${colors[color]} flex items-center justify-center`}>
            <Icon className="h-6 w-6" />
          </div>
        </div>
      </CardContent>
    </Card>
  )
}
