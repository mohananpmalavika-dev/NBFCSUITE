'use client'

import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Textarea } from '@/components/ui/textarea'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from '@/components/ui/dialog'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { Checkbox } from '@/components/ui/checkbox'
import { 
  Clock, 
  Plus, 
  Filter,
  Search,
  Star,
  User,
  FileText,
  CreditCard,
  AlertCircle,
  Loader2
} from 'lucide-react'
import { useToast } from '@/components/ui/use-toast'
import { customerService } from '@/services/customer.service'
import type { CustomerTimeline } from '@/types/customer.types'
import { formatDate } from '@/lib/utils'

interface CustomerTimelineProps {
  customerId: string
}

export function CustomerTimelineComponent({ customerId }: CustomerTimelineProps) {
  const { toast } = useToast()
  const queryClient = useQueryClient()
  const [dialogOpen, setDialogOpen] = useState(false)
  const [filterCategory, setFilterCategory] = useState<string>('all')
  const [importantOnly, setImportantOnly] = useState(false)

  // Fetch timeline
  const { data: timeline, isLoading } = useQuery({
    queryKey: ['customer-timeline', customerId, filterCategory, importantOnly],
    queryFn: () => customerService.getTimeline(customerId, {
      page: 1,
      page_size: 50,
      event_category: filterCategory !== 'all' ? filterCategory : undefined,
      important_only: importantOnly,
    }),
  })

  // Fetch activity summary
  const { data: summary } = useQuery({
    queryKey: ['timeline-summary', customerId],
    queryFn: () => customerService.getActivitySummary(customerId, 30),
  })

  const activities = timeline?.data?.items || []

  const getActivityIcon = (type: string) => {
    switch (type.toLowerCase()) {
      case 'customer_created':
      case 'customer_updated':
        return <User className="h-4 w-4" />
      case 'kyc_initiated':
      case 'kyc_completed':
        return <FileText className="h-4 w-4" />
      case 'document_uploaded':
      case 'document_verified':
        return <FileText className="h-4 w-4" />
      case 'bureau_pulled':
        return <CreditCard className="h-4 w-4" />
      default:
        return <Clock className="h-4 w-4" />
    }
  }

  const getActivityColor = (type: string) => {
    switch (type.toLowerCase()) {
      case 'customer_created':
        return 'bg-blue-100 text-blue-800'
      case 'kyc_completed':
      case 'document_verified':
        return 'bg-green-100 text-green-800'
      case 'kyc_initiated':
        return 'bg-yellow-100 text-yellow-800'
      default:
        return 'bg-gray-100 text-gray-800'
    }
  }

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-12">
        <Loader2 className="h-8 w-8 animate-spin text-gray-400" />
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle className="flex items-center gap-2">
                <Clock className="h-5 w-5" />
                Activity Timeline
              </CardTitle>
              <CardDescription>
                Track all customer activities and interactions
              </CardDescription>
            </div>
            <Button onClick={() => setDialogOpen(true)}>
              <Plus className="h-4 w-4 mr-2" />
              Add Note
            </Button>
          </div>
        </CardHeader>
      </Card>

      {/* Filters */}
      <Card>
        <CardContent className="pt-6">
          <div className="flex items-center gap-4">
            <div className="flex-1">
              <Label htmlFor="category">Filter by Category</Label>
              <Select value={filterCategory} onValueChange={setFilterCategory}>
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Activities</SelectItem>
                  <SelectItem value="kyc">KYC</SelectItem>
                  <SelectItem value="document">Documents</SelectItem>
                  <SelectItem value="loan">Loans</SelectItem>
                  <SelectItem value="payment">Payments</SelectItem>
                  <SelectItem value="bureau">Credit Bureau</SelectItem>
                  <SelectItem value="note">Notes</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div className="flex items-center space-x-2 pt-6">
              <Checkbox
                id="important"
                checked={importantOnly}
                onCheckedChange={(checked) => setImportantOnly(!!checked)}
              />
              <Label htmlFor="important" className="font-normal cursor-pointer">
                Important only
              </Label>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Activity Summary */}
      {summary?.data && (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {Object.entries(summary.data.activity_counts).map(([type, count]) => (
            <Card key={type}>
              <CardContent className="pt-6">
                <div className="text-center">
                  <p className="text-2xl font-bold text-gray-900">{count as number}</p>
                  <p className="text-sm text-gray-600 mt-1 capitalize">
                    {type.replace('_', ' ')}
                  </p>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      {/* Timeline */}
      <Card>
        <CardContent className="pt-6">
          {activities.length === 0 ? (
            <div className="text-center py-12">
              <Clock className="h-12 w-12 mx-auto text-gray-400 mb-4" />
              <p className="text-gray-600">No activities found</p>
            </div>
          ) : (
            <div className="relative">
              {/* Timeline Line */}
              <div className="absolute left-6 top-0 bottom-0 w-0.5 bg-gray-200" />

              {/* Timeline Items */}
              <div className="space-y-6">
                {activities.map((activity, index) => (
                  <div key={activity.id} className="relative flex gap-4">
                    {/* Timeline Dot */}
                    <div className={`relative z-10 flex-shrink-0 w-12 h-12 rounded-full flex items-center justify-center ${getActivityColor(activity.activity_type)}`}>
                      {getActivityIcon(activity.activity_type)}
                      {activity.is_important && (
                        <Star className="absolute -top-1 -right-1 h-4 w-4 text-yellow-500 fill-yellow-500" />
                      )}
                    </div>

                    {/* Content */}
                    <div className="flex-1 pb-6">
                      <div className="bg-white border rounded-lg p-4">
                        <div className="flex items-start justify-between mb-2">
                          <div>
                            <h4 className="font-semibold text-gray-900">{activity.title}</h4>
                            <p className="text-sm text-gray-600 mt-1">
                              {formatDate(activity.event_date)}
                              {activity.performed_by_name && (
                                <> • by {activity.performed_by_name}</>
                              )}
                              {activity.performed_by_role && (
                                <> ({activity.performed_by_role})</>
                              )}
                            </p>
                          </div>
                          <Badge className={getActivityColor(activity.activity_type)}>
                            {activity.activity_type.replace(/_/g, ' ')}
                          </Badge>
                        </div>

                        {activity.description && (
                          <p className="text-sm text-gray-700 mt-2">{activity.description}</p>
                        )}

                        {activity.changes && Object.keys(activity.changes).length > 0 && (
                          <div className="mt-3 p-3 bg-gray-50 rounded border text-sm">
                            <p className="font-medium text-gray-700 mb-2">Changes:</p>
                            <div className="space-y-1">
                              {Object.entries(activity.changes).map(([key, value]: [string, any]) => (
                                <div key={key} className="flex items-center gap-2">
                                  <span className="text-gray-600">{key}:</span>
                                  <span className="text-red-600 line-through">{value.old}</span>
                                  <span className="text-gray-400">→</span>
                                  <span className="text-green-600">{value.new}</span>
                                </div>
                              ))}
                            </div>
                          </div>
                        )}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Add Note Dialog */}
      <AddNoteDialog
        open={dialogOpen}
        onOpenChange={setDialogOpen}
        customerId={customerId}
      />
    </div>
  )
}

function AddNoteDialog({
  open,
  onOpenChange,
  customerId,
}: {
  open: boolean
  onOpenChange: (open: boolean) => void
  customerId: string
}) {
  const { toast } = useToast()
  const queryClient = useQueryClient()
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    event_category: 'note',
    is_important: false,
  })

  const addNoteMutation = useMutation({
    mutationFn: () => customerService.logActivity(customerId, {
      activity_type: 'note_added',
      ...formData,
    }),
    onSuccess: () => {
      toast({
        title: 'Note Added',
        description: 'Activity note added successfully',
      })
      queryClient.invalidateQueries({ queryKey: ['customer-timeline', customerId] })
      onOpenChange(false)
      setFormData({
        title: '',
        description: '',
        event_category: 'note',
        is_important: false,
      })
    },
    onError: (error: any) => {
      toast({
        title: 'Failed to add note',
        description: error.response?.data?.detail || 'An error occurred',
        variant: 'destructive',
      })
    },
  })

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Add Activity Note</DialogTitle>
          <DialogDescription>
            Add a manual note or activity to the timeline
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="title">Title *</Label>
            <Input
              id="title"
              value={formData.title}
              onChange={(e) => setFormData({ ...formData, title: e.target.value })}
              placeholder="Enter note title"
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="description">Description</Label>
            <Textarea
              id="description"
              value={formData.description}
              onChange={(e) => setFormData({ ...formData, description: e.target.value })}
              placeholder="Enter detailed description"
              rows={4}
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="category">Category</Label>
            <Select
              value={formData.event_category}
              onValueChange={(value) => setFormData({ ...formData, event_category: value })}
            >
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="note">General Note</SelectItem>
                <SelectItem value="call">Phone Call</SelectItem>
                <SelectItem value="meeting">Meeting</SelectItem>
                <SelectItem value="email">Email</SelectItem>
                <SelectItem value="kyc">KYC</SelectItem>
                <SelectItem value="document">Document</SelectItem>
              </SelectContent>
            </Select>
          </div>

          <div className="flex items-center space-x-2">
            <Checkbox
              id="important"
              checked={formData.is_important}
              onCheckedChange={(checked) => setFormData({ ...formData, is_important: !!checked })}
            />
            <Label htmlFor="important" className="font-normal cursor-pointer">
              Mark as important
            </Label>
          </div>
        </div>

        <DialogFooter>
          <Button variant="outline" onClick={() => onOpenChange(false)}>
            Cancel
          </Button>
          <Button
            onClick={() => addNoteMutation.mutate()}
            disabled={!formData.title || addNoteMutation.isPending}
          >
            {addNoteMutation.isPending && (
              <Loader2 className="h-4 w-4 mr-2 animate-spin" />
            )}
            Add Note
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}
