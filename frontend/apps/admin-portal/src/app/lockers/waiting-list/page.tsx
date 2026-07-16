'use client'

import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { 
  Plus, Search, Filter, Eye, Clock, TrendingUp, Users, 
  Send, CheckCircle, XCircle, AlertCircle, ArrowUpDown, Timer
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
  waitingListService, 
  WaitingListStatus,
  type LockerWaitingList 
} from '@/services/locker.service'
import { formatCurrency, formatDate } from '@/lib/utils'
import { toast } from 'sonner'

export default function WaitingListPage() {
  const [page, setPage] = useState(1)
  const [search, setSearch] = useState('')
  const [statusFilter, setStatusFilter] = useState<WaitingListStatus | ''>('')
  const [isAddOpen, setIsAddOpen] = useState(false)
  const [isOfferOpen, setIsOfferOpen] = useState(false)
  const [isViewOpen, setIsViewOpen] = useState(false)
  const [selectedEntry, setSelectedEntry] = useState<LockerWaitingList | null>(null)
  const [activeTab, setActiveTab] = useState('all')

  const queryClient = useQueryClient()

  const { data, isLoading } = useQuery({
    queryKey: ['waiting-list', page, search, statusFilter, activeTab],
    queryFn: () => {
      const params: any = {
        skip: (page - 1) * 12,
        limit: 12,
      }
      if (statusFilter) params.status = statusFilter
      if (activeTab === 'active') params.status = WaitingListStatus.ACTIVE
      if (activeTab === 'offered') params.status = WaitingListStatus.OFFER_MADE
      return waitingListService.listWaitingList(params)
    },
  })

  const { data: analyticsData } = useQuery({
    queryKey: ['waiting-list-analytics'],
    queryFn: () => waitingListService.getAnalytics(),
  })

  const { data: statisticsData } = useQuery({
    queryKey: ['waiting-list-statistics'],
    queryFn: () => waitingListService.getStatistics(),
  })

  const { data: nextInQueueData } = useQuery({
    queryKey: ['waiting-list-next'],
    queryFn: () => waitingListService.getNextInQueue({ size: 'small' }),
  })

  const addMutation = useMutation({
    mutationFn: (data: any) => waitingListService.addToWaitingList(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['waiting-list'] })
      setIsAddOpen(false)
      toast.success('Added to waiting list successfully')
    },
    onError: () => {
      toast.error('Failed to add to waiting list')
    },
  })

  const makeOfferMutation = useMutation({
    mutationFn: ({ id, data }: { id: string; data: any }) =>
      waitingListService.makeOffer(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['waiting-list'] })
      setIsOfferOpen(false)
      toast.success('Offer sent successfully')
    },
    onError: () => {
      toast.error('Failed to send offer')
    },
  })

  const removeMutation = useMutation({
    mutationFn: (id: string) => waitingListService.removeFromWaitingList(id, 'Customer request'),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['waiting-list'] })
      toast.success('Removed from waiting list')
    },
    onError: () => {
      toast.error('Failed to remove from waiting list')
    },
  })

  const getStatusColor = (status: WaitingListStatus) => {
    const colors = {
      active: 'bg-green-100 text-green-800',
      offer_made: 'bg-blue-100 text-blue-800',
      offer_accepted: 'bg-purple-100 text-purple-800',
      offer_declined: 'bg-red-100 text-red-800',
      offer_expired: 'bg-yellow-100 text-yellow-800',
      allocated: 'bg-teal-100 text-teal-800',
      removed: 'bg-gray-100 text-gray-800',
    }
    return colors[status] || 'bg-gray-100 text-gray-800'
  }

  const handleView = (entry: LockerWaitingList) => {
    setSelectedEntry(entry)
    setIsViewOpen(true)
  }

  const handleMakeOffer = (entry: LockerWaitingList) => {
    setSelectedEntry(entry)
    setIsOfferOpen(true)
  }

  const handleRemove = (entry: LockerWaitingList) => {
    if (confirm('Are you sure you want to remove this entry from the waiting list?')) {
      removeMutation.mutate(entry.id)
    }
  }

  return (
    <DashboardLayout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Waiting List</h1>
            <p className="text-gray-600 mt-1">Manage priority queue and locker offers</p>
          </div>
          <Button onClick={() => setIsAddOpen(true)}>
            <Plus className="h-4 w-4 mr-2" />
            Add to Waiting List
          </Button>
        </div>

        {/* Statistics Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <Card className="border-l-4 border-l-blue-500">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Total in Queue</CardTitle>
              <Users className="h-4 w-4 text-blue-600" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-blue-600">
                {statisticsData?.data?.total_entries || 0}
              </div>
              <p className="text-xs text-gray-600 mt-1">Waiting for locker</p>
            </CardContent>
          </Card>

          <Card className="border-l-4 border-l-green-500">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Active Entries</CardTitle>
              <CheckCircle className="h-4 w-4 text-green-600" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-green-600">
                {statisticsData?.data?.active_entries || 0}
              </div>
              <p className="text-xs text-gray-600 mt-1">In queue</p>
            </CardContent>
          </Card>

          <Card className="border-l-4 border-l-yellow-500">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Offers Pending</CardTitle>
              <Clock className="h-4 w-4 text-yellow-600" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-yellow-600">
                {statisticsData?.data?.offers_pending || 0}
              </div>
              <p className="text-xs text-gray-600 mt-1">Awaiting response</p>
            </CardContent>
          </Card>

          <Card className="border-l-4 border-l-purple-500">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Avg Wait Time</CardTitle>
              <Timer className="h-4 w-4 text-purple-600" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-purple-600">
                {statisticsData?.data?.average_waiting_days?.toFixed(0) || 0}
              </div>
              <p className="text-xs text-gray-600 mt-1">Days</p>
            </CardContent>
          </Card>
        </div>

        {/* Priority Queue Info */}
        {analyticsData?.data && (
          <Card className="bg-gradient-to-r from-blue-50 to-purple-50">
            <CardContent className="pt-6">
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="flex items-start gap-3">
                  <div className="p-2 bg-blue-100 rounded-lg">
                    <TrendingUp className="h-5 w-5 text-blue-600" />
                  </div>
                  <div>
                    <p className="text-sm text-gray-600">Highest Priority</p>
                    <p className="text-xl font-bold text-gray-900">
                      {analyticsData.data.highest_priority_score?.toFixed(0) || 0}
                    </p>
                  </div>
                </div>
                <div className="flex items-start gap-3">
                  <div className="p-2 bg-purple-100 rounded-lg">
                    <ArrowUpDown className="h-5 w-5 text-purple-600" />
                  </div>
                  <div>
                    <p className="text-sm text-gray-600">Average Priority</p>
                    <p className="text-xl font-bold text-gray-900">
                      {analyticsData.data.average_priority_score?.toFixed(0) || 0}
                    </p>
                  </div>
                </div>
                <div className="flex items-start gap-3">
                  <div className="p-2 bg-green-100 rounded-lg">
                    <Send className="h-5 w-5 text-green-600" />
                  </div>
                  <div>
                    <p className="text-sm text-gray-600">Offers Made</p>
                    <p className="text-xl font-bold text-gray-900">
                      {analyticsData.data.total_offers_made || 0}
                    </p>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        )}

        {/* Tabs */}
        <Tabs value={activeTab} onValueChange={setActiveTab}>
          <TabsList>
            <TabsTrigger value="all">All Entries</TabsTrigger>
            <TabsTrigger value="active">Active Queue</TabsTrigger>
            <TabsTrigger value="offered">Offers Made</TabsTrigger>
          </TabsList>

          <TabsContent value={activeTab} className="space-y-4">
            {/* Filters */}
            <div className="flex items-center gap-4">
              <div className="flex-1 relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
                <Input
                  type="search"
                  placeholder="Search by customer ID, application number..."
                  className="pl-10"
                  value={search}
                  onChange={(e) => setSearch(e.target.value)}
                />
              </div>
              <Select value={statusFilter} onValueChange={(value) => setStatusFilter(value as WaitingListStatus | '')}>
                <SelectTrigger className="w-[200px]">
                  <SelectValue placeholder="All Status" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="">All Status</SelectItem>
                  <SelectItem value={WaitingListStatus.ACTIVE}>Active</SelectItem>
                  <SelectItem value={WaitingListStatus.OFFER_MADE}>Offer Made</SelectItem>
                  <SelectItem value={WaitingListStatus.OFFER_ACCEPTED}>Offer Accepted</SelectItem>
                  <SelectItem value={WaitingListStatus.OFFER_DECLINED}>Offer Declined</SelectItem>
                  <SelectItem value={WaitingListStatus.ALLOCATED}>Allocated</SelectItem>
                </SelectContent>
              </Select>
              <Button variant="outline">
                <Filter className="h-4 w-4 mr-2" />
                More Filters
              </Button>
            </div>

            {/* Waiting List Table */}
            <Card>
              <CardContent className="p-0">
                <div className="overflow-x-auto">
                  <table className="w-full">
                    <thead className="bg-gray-50 border-b">
                      <tr>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                          Position
                        </th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                          Customer
                        </th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                          Application
                        </th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                          Preferences
                        </th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                          Priority
                        </th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                          Wait Time
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
                            <td className="px-6 py-4"><Skeleton className="h-4 w-12" /></td>
                            <td className="px-6 py-4"><Skeleton className="h-4 w-32" /></td>
                            <td className="px-6 py-4"><Skeleton className="h-4 w-32" /></td>
                            <td className="px-6 py-4"><Skeleton className="h-4 w-24" /></td>
                            <td className="px-6 py-4"><Skeleton className="h-4 w-16" /></td>
                            <td className="px-6 py-4"><Skeleton className="h-4 w-20" /></td>
                            <td className="px-6 py-4"><Skeleton className="h-6 w-24" /></td>
                            <td className="px-6 py-4"><Skeleton className="h-8 w-24" /></td>
                          </tr>
                        ))
                      ) : data?.data?.entries && data.data.entries.length > 0 ? (
                        data.data.entries.map((entry: LockerWaitingList) => (
                          <tr key={entry.id} className="hover:bg-gray-50">
                            <td className="px-6 py-4 whitespace-nowrap">
                              <div className="flex items-center gap-2">
                                <div className="w-8 h-8 rounded-full bg-blue-100 text-blue-700 font-bold flex items-center justify-center text-sm">
                                  {entry.queue_position}
                                </div>
                              </div>
                            </td>
                            <td className="px-6 py-4">
                              <div className="text-sm font-medium text-gray-900">
                                ID: {entry.customer_id}
                              </div>
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap">
                              <div className="text-sm text-gray-900">
                                {entry.application_id}
                              </div>
                              <div className="text-xs text-gray-500">
                                {formatDate(entry.added_date)}
                              </div>
                            </td>
                            <td className="px-6 py-4">
                              <div className="text-sm text-gray-900">
                                Size: {entry.preferred_size}
                              </div>
                              {entry.preferred_location && (
                                <div className="text-xs text-gray-500">
                                  Loc: {entry.preferred_location}
                                </div>
                              )}
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap">
                              <div className="text-sm font-medium text-gray-900">
                                {entry.priority_score}
                              </div>
                              <div className="text-xs text-gray-500">/ 100</div>
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap">
                              <div className="text-sm text-gray-900">
                                {entry.waiting_days || 0} days
                              </div>
                              {entry.estimated_wait_days && (
                                <div className="text-xs text-gray-500">
                                  Est: {entry.estimated_wait_days}d
                                </div>
                              )}
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap">
                              <Badge className={getStatusColor(entry.status)}>
                                {entry.status.replace('_', ' ').toUpperCase()}
                              </Badge>
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap text-right">
                              <div className="flex items-center justify-end gap-2">
                                <Button
                                  variant="ghost"
                                  size="sm"
                                  onClick={() => handleView(entry)}
                                >
                                  <Eye className="h-4 w-4" />
                                </Button>
                                {entry.status === WaitingListStatus.ACTIVE && (
                                  <Button
                                    variant="ghost"
                                    size="sm"
                                    className="text-blue-600"
                                    onClick={() => handleMakeOffer(entry)}
                                  >
                                    <Send className="h-4 w-4" />
                                  </Button>
                                )}
                                {(entry.status === WaitingListStatus.ACTIVE || 
                                  entry.status === WaitingListStatus.OFFER_DECLINED) && (
                                  <Button
                                    variant="ghost"
                                    size="sm"
                                    className="text-red-600"
                                    onClick={() => handleRemove(entry)}
                                  >
                                    <XCircle className="h-4 w-4" />
                                  </Button>
                                )}
                              </div>
                            </td>
                          </tr>
                        ))
                      ) : (
                        <tr>
                          <td colSpan={8} className="px-6 py-12 text-center text-gray-500">
                            No entries in waiting list
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
        <AddToWaitingListDialog
          open={isAddOpen}
          onOpenChange={setIsAddOpen}
          onSubmit={(data) => addMutation.mutate(data)}
          isLoading={addMutation.isPending}
        />

        {selectedEntry && (
          <>
            <MakeOfferDialog
              open={isOfferOpen}
              onOpenChange={setIsOfferOpen}
              entry={selectedEntry}
              onSubmit={(data) => makeOfferMutation.mutate({ id: selectedEntry.id, data })}
              isLoading={makeOfferMutation.isPending}
            />
            <ViewEntryDialog
              open={isViewOpen}
              onOpenChange={setIsViewOpen}
              entry={selectedEntry}
            />
          </>
        )}
      </div>
    </DashboardLayout>
  )
}

// Add to Waiting List Dialog Component
function AddToWaitingListDialog({
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
  const [formData, setFormData] = useState<any>({
    application_id: '',
    customer_id: '',
    preferred_size: 'small',
    preferred_location: '',
    added_date: new Date().toISOString().split('T')[0],
    priority_score: 0,
    remarks: '',
  })

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    onSubmit(formData)
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-2xl">
        <DialogHeader>
          <DialogTitle>Add to Waiting List</DialogTitle>
          <DialogDescription>Add a customer to the priority queue</DialogDescription>
        </DialogHeader>

        <form onSubmit={handleSubmit} className="space-y-6">
          <div className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="application_id">Application ID *</Label>
                <Input
                  id="application_id"
                  value={formData.application_id}
                  onChange={(e) => setFormData({ ...formData, application_id: e.target.value })}
                  required
                  placeholder="Search application..."
                />
              </div>
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
            </div>

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
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="added_date">Added Date</Label>
                <Input
                  id="added_date"
                  type="date"
                  value={formData.added_date}
                  onChange={(e) => setFormData({ ...formData, added_date: e.target.value })}
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="priority_score">Priority Score</Label>
                <Input
                  id="priority_score"
                  type="number"
                  min="0"
                  max="100"
                  value={formData.priority_score}
                  onChange={(e) => setFormData({ ...formData, priority_score: parseInt(e.target.value) })}
                  placeholder="Auto-calculated"
                />
                <p className="text-xs text-gray-500">Leave blank for automatic calculation</p>
              </div>
            </div>

            <div className="space-y-2">
              <Label htmlFor="remarks">Remarks</Label>
              <Textarea
                id="remarks"
                value={formData.remarks}
                onChange={(e) => setFormData({ ...formData, remarks: e.target.value })}
                placeholder="Any additional notes..."
                rows={3}
              />
            </div>
          </div>

          <DialogFooter>
            <Button type="button" variant="outline" onClick={() => onOpenChange(false)}>
              Cancel
            </Button>
            <Button type="submit" disabled={isLoading}>
              {isLoading ? 'Adding...' : 'Add to Queue'}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  )
}

// Make Offer Dialog Component
function MakeOfferDialog({
  open,
  onOpenChange,
  entry,
  onSubmit,
  isLoading,
}: {
  open: boolean
  onOpenChange: (open: boolean) => void
  entry: LockerWaitingList
  onSubmit: (data: any) => void
  isLoading: boolean
}) {
  const [formData, setFormData] = useState<any>({
    locker_id: '',
    offer_date: new Date().toISOString().split('T')[0],
    offer_expiry_date: new Date(Date.now() + 7 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
    offered_rent: 0,
    remarks: '',
  })

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    onSubmit(formData)
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-2xl">
        <DialogHeader>
          <DialogTitle>Make Locker Offer</DialogTitle>
          <DialogDescription>
            Send locker offer to customer (Position #{entry.queue_position})
          </DialogDescription>
        </DialogHeader>

        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Entry Summary */}
          <Card className="bg-blue-50 border-blue-200">
            <CardContent className="pt-6">
              <div className="grid grid-cols-2 gap-4 text-sm">
                <div>
                  <p className="text-gray-600">Customer ID</p>
                  <p className="font-medium">{entry.customer_id}</p>
                </div>
                <div>
                  <p className="text-gray-600">Queue Position</p>
                  <p className="font-medium">#{entry.queue_position}</p>
                </div>
                <div>
                  <p className="text-gray-600">Preferred Size</p>
                  <p className="font-medium">{entry.preferred_size}</p>
                </div>
                <div>
                  <p className="text-gray-600">Priority Score</p>
                  <p className="font-medium">{entry.priority_score}</p>
                </div>
                <div>
                  <p className="text-gray-600">Waiting Days</p>
                  <p className="font-medium">{entry.waiting_days || 0} days</p>
                </div>
                <div>
                  <p className="text-gray-600">Application</p>
                  <p className="font-medium">{entry.application_id}</p>
                </div>
              </div>
            </CardContent>
          </Card>

          <div className="space-y-4">
            <h3 className="text-sm font-medium">Offer Details</h3>
            
            <div className="space-y-2">
              <Label htmlFor="locker_id">Locker ID *</Label>
              <Input
                id="locker_id"
                value={formData.locker_id}
                onChange={(e) => setFormData({ ...formData, locker_id: e.target.value })}
                required
                placeholder="Select available locker..."
              />
              <p className="text-xs text-gray-500">Select a locker matching the preferred size</p>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="offer_date">Offer Date</Label>
                <Input
                  id="offer_date"
                  type="date"
                  value={formData.offer_date}
                  onChange={(e) => setFormData({ ...formData, offer_date: e.target.value })}
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="offer_expiry_date">Expiry Date *</Label>
                <Input
                  id="offer_expiry_date"
                  type="date"
                  value={formData.offer_expiry_date}
                  onChange={(e) => setFormData({ ...formData, offer_expiry_date: e.target.value })}
                  required
                />
              </div>
            </div>

            <div className="space-y-2">
              <Label htmlFor="offered_rent">Annual Rent (₹) *</Label>
              <Input
                id="offered_rent"
                type="number"
                min="0"
                value={formData.offered_rent}
                onChange={(e) => setFormData({ ...formData, offered_rent: parseFloat(e.target.value) })}
                required
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="remarks">Remarks</Label>
              <Textarea
                id="remarks"
                value={formData.remarks}
                onChange={(e) => setFormData({ ...formData, remarks: e.target.value })}
                placeholder="Any special terms or conditions..."
                rows={3}
              />
            </div>
          </div>

          <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
            <div className="flex items-start gap-3">
              <AlertCircle className="h-5 w-5 text-yellow-600 mt-0.5" />
              <div className="text-sm text-yellow-900">
                <p className="font-medium mb-1">Before Making Offer</p>
                <ul className="list-disc list-inside space-y-1 text-yellow-800">
                  <li>Verify the locker is available and matches preferences</li>
                  <li>Confirm rent amount with current pricing policy</li>
                  <li>Customer will be notified via email and SMS</li>
                  <li>Offer expires in 7 days by default</li>
                </ul>
              </div>
            </div>
          </div>

          <DialogFooter>
            <Button type="button" variant="outline" onClick={() => onOpenChange(false)}>
              Cancel
            </Button>
            <Button type="submit" disabled={isLoading} className="bg-blue-600 hover:bg-blue-700">
              {isLoading ? 'Sending...' : 'Send Offer'}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  )
}

// View Entry Dialog Component
function ViewEntryDialog({
  open,
  onOpenChange,
  entry,
}: {
  open: boolean
  onOpenChange: (open: boolean) => void
  entry: LockerWaitingList
}) {
  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-3xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>Waiting List Entry Details</DialogTitle>
          <DialogDescription>
            Queue Position #{entry.queue_position}
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-6">
          {/* Status Banner */}
          <div className={`p-4 rounded-lg border-l-4 ${
            entry.status === WaitingListStatus.ACTIVE ? 'bg-green-50 border-green-500' :
            entry.status === WaitingListStatus.OFFER_MADE ? 'bg-blue-50 border-blue-500' :
            entry.status === WaitingListStatus.ALLOCATED ? 'bg-purple-50 border-purple-500' :
            'bg-gray-50 border-gray-500'
          }`}>
            <div className="flex items-center justify-between">
              <div>
                <p className="font-medium">Status: {entry.status.replace('_', ' ').toUpperCase()}</p>
                <p className="text-sm mt-1">Position: #{entry.queue_position}</p>
              </div>
              <Badge className="text-lg px-3 py-1">
                Priority: {entry.priority_score}
              </Badge>
            </div>
          </div>

          {/* Basic Information */}
          <div className="space-y-3">
            <h3 className="font-medium text-gray-900">Basic Information</h3>
            <div className="grid grid-cols-2 gap-4 text-sm">
              <div>
                <p className="text-gray-500">Customer ID</p>
                <p className="font-medium">{entry.customer_id}</p>
              </div>
              <div>
                <p className="text-gray-500">Application ID</p>
                <p className="font-medium">{entry.application_id}</p>
              </div>
              <div>
                <p className="text-gray-500">Added Date</p>
                <p className="font-medium">{formatDate(entry.added_date)}</p>
              </div>
              <div>
                <p className="text-gray-500">Branch</p>
                <p className="font-medium">{entry.branch_id || 'N/A'}</p>
              </div>
            </div>
          </div>

          {/* Preferences */}
          <div className="space-y-3 border-t pt-4">
            <h3 className="font-medium text-gray-900">Locker Preferences</h3>
            <div className="grid grid-cols-2 gap-4 text-sm">
              <div>
                <p className="text-gray-500">Preferred Size</p>
                <p className="font-medium">{entry.preferred_size}</p>
              </div>
              <div>
                <p className="text-gray-500">Preferred Location</p>
                <p className="font-medium">{entry.preferred_location || 'Any'}</p>
              </div>
            </div>
          </div>

          {/* Queue Information */}
          <div className="space-y-3 border-t pt-4">
            <h3 className="font-medium text-gray-900">Queue Information</h3>
            <div className="grid grid-cols-3 gap-4 text-sm">
              <div>
                <p className="text-gray-500">Queue Position</p>
                <p className="font-medium text-lg">#{entry.queue_position}</p>
              </div>
              <div>
                <p className="text-gray-500">Priority Score</p>
                <p className="font-medium text-lg">{entry.priority_score}</p>
              </div>
              <div>
                <p className="text-gray-500">Waiting Days</p>
                <p className="font-medium text-lg">{entry.waiting_days || 0}</p>
              </div>
            </div>
            {entry.estimated_wait_days && (
              <div className="bg-blue-50 rounded-lg p-3">
                <p className="text-sm text-blue-900">
                  <Clock className="h-4 w-4 inline mr-2" />
                  Estimated wait time: <strong>{entry.estimated_wait_days} days</strong>
                </p>
              </div>
            )}
          </div>

          {/* Offer Information */}
          {entry.offer_details && (
            <div className="space-y-3 border-t pt-4">
              <h3 className="font-medium text-gray-900">Offer Information</h3>
              <div className="bg-gray-50 rounded-lg p-4 space-y-3">
                <div className="grid grid-cols-2 gap-4 text-sm">
                  {entry.offer_details.locker_id && (
                    <div>
                      <p className="text-gray-500">Offered Locker</p>
                      <p className="font-medium">{entry.offer_details.locker_id}</p>
                    </div>
                  )}
                  {entry.offer_details.offer_date && (
                    <div>
                      <p className="text-gray-500">Offer Date</p>
                      <p className="font-medium">{formatDate(entry.offer_details.offer_date)}</p>
                    </div>
                  )}
                  {entry.offer_details.offer_expiry_date && (
                    <div>
                      <p className="text-gray-500">Expiry Date</p>
                      <p className="font-medium">{formatDate(entry.offer_details.offer_expiry_date)}</p>
                    </div>
                  )}
                  {entry.offer_details.offered_rent && (
                    <div>
                      <p className="text-gray-500">Offered Rent</p>
                      <p className="font-medium">{formatCurrency(entry.offer_details.offered_rent)}/year</p>
                    </div>
                  )}
                </div>
                {entry.offer_details.customer_response_date && (
                  <div className="border-t pt-3">
                    <p className="text-sm text-gray-600">
                      Customer Response: <strong>{entry.offer_details.customer_response}</strong>
                    </p>
                    <p className="text-xs text-gray-500 mt-1">
                      Responded on: {formatDate(entry.offer_details.customer_response_date)}
                    </p>
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Priority Breakdown */}
          {entry.priority_breakdown && (
            <div className="space-y-3 border-t pt-4">
              <h3 className="font-medium text-gray-900">Priority Score Breakdown</h3>
              <div className="bg-gray-50 rounded-lg p-4 space-y-2 text-sm">
                {Object.entries(entry.priority_breakdown).map(([key, value]) => (
                  <div key={key} className="flex justify-between">
                    <span className="text-gray-600">{key.replace('_', ' ')}</span>
                    <span className="font-medium">{value} pts</span>
                  </div>
                ))}
                <div className="flex justify-between border-t pt-2 font-medium">
                  <span>Total Score</span>
                  <span>{entry.priority_score}</span>
                </div>
              </div>
            </div>
          )}

          {/* Remarks */}
          {entry.remarks && (
            <div className="space-y-2 border-t pt-4">
              <h3 className="font-medium text-gray-900">Remarks</h3>
              <p className="text-sm text-gray-700">{entry.remarks}</p>
            </div>
          )}

          {/* Timeline */}
          <div className="space-y-3 border-t pt-4">
            <h3 className="font-medium text-gray-900">Timeline</h3>
            <div className="space-y-2">
              <div className="flex items-center gap-3 text-sm">
                <div className="w-2 h-2 rounded-full bg-green-500"></div>
                <div className="flex-1">
                  <p className="font-medium">Added to Queue</p>
                  <p className="text-xs text-gray-500">{formatDate(entry.added_date)}</p>
                </div>
              </div>
              {entry.last_position_update && (
                <div className="flex items-center gap-3 text-sm">
                  <div className="w-2 h-2 rounded-full bg-blue-500"></div>
                  <div className="flex-1">
                    <p className="font-medium">Position Updated</p>
                    <p className="text-xs text-gray-500">{formatDate(entry.last_position_update)}</p>
                  </div>
                </div>
              )}
              {entry.offer_details?.offer_date && (
                <div className="flex items-center gap-3 text-sm">
                  <div className="w-2 h-2 rounded-full bg-purple-500"></div>
                  <div className="flex-1">
                    <p className="font-medium">Offer Made</p>
                    <p className="text-xs text-gray-500">{formatDate(entry.offer_details.offer_date)}</p>
                  </div>
                </div>
              )}
            </div>
          </div>
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
