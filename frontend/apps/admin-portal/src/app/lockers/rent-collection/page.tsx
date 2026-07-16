'use client'

import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { 
  Plus, Calculator, Send, Receipt, DollarSign, Clock,
  TrendingUp, AlertCircle, Download, RefreshCw, Calendar
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
import { 
  rentCollectionService,
  type RentCalculation,
  type OverdueAllocation,
  type UpcomingDue
} from '@/services/locker.service'
import { formatCurrency, formatDate } from '@/lib/utils'
import { toast } from 'sonner'

export default function RentCollectionPage() {
  const [isCollectOpen, setIsCollectOpen] = useState(false)
  const [isCalculateOpen, setIsCalculateOpen] = useState(false)
  const [isReminderOpen, setIsReminderOpen] = useState(false)
  const [selectedAllocation, setSelectedAllocation] = useState<string>('')
  const [calculationType, setCalculationType] = useState<'annual' | 'prorata' | 'advance'>('annual')
  const [activeTab, setActiveTab] = useState('overview')

  const queryClient = useQueryClient()

  // Queries
  const { data: overdueData } = useQuery({
    queryKey: ['overdue-allocations'],
    queryFn: () => rentCollectionService.getOverdueAllocations(),
  })

  const { data: upcomingData } = useQuery({
    queryKey: ['upcoming-due'],
    queryFn: () => rentCollectionService.getUpcomingDueDates(30),
  })

  const { data: collectionSummary } = useQuery({
    queryKey: ['collection-summary'],
    queryFn: () => rentCollectionService.getRentCollectionSummary(),
  })

  // Mutations
  const collectRentMutation = useMutation({
    mutationFn: (data: any) => rentCollectionService.collectRent(data.allocationId, data.paymentData),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['overdue-allocations'] })
      queryClient.invalidateQueries({ queryKey: ['collection-summary'] })
      setIsCollectOpen(false)
      toast.success('Rent collected successfully')
    },
    onError: () => {
      toast.error('Failed to collect rent')
    },
  })

  const sendReminderMutation = useMutation({
    mutationFn: (data: any) => 
      rentCollectionService.sendRentReminder(data.allocationId, data.reminderType, data.daysBeforeDue),
    onSuccess: () => {
      setIsReminderOpen(false)
      toast.success('Reminder sent successfully')
    },
    onError: () => {
      toast.error('Failed to send reminder')
    },
  })

  const sendBulkRemindersMutation = useMutation({
    mutationFn: (data: any) => 
      rentCollectionService.sendBulkReminders(data.reminderType, data.daysBeforeDue),
    onSuccess: (result: any) => {
      toast.success(`Sent ${result.data.sent_count} reminders successfully`)
    },
    onError: () => {
      toast.error('Failed to send bulk reminders')
    },
  })

  return (
    <DashboardLayout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Rent Collection</h1>
            <p className="text-gray-600 mt-1">Manage locker rent payments, calculations, and reminders</p>
          </div>
          <div className="flex gap-2">
            <Button variant="outline" onClick={() => setIsReminderOpen(true)}>
              <Send className="h-4 w-4 mr-2" />
              Send Reminders
            </Button>
            <Button onClick={() => setIsCollectOpen(true)}>
              <Plus className="h-4 w-4 mr-2" />
              Collect Rent
            </Button>
          </div>
        </div>

        {/* Statistics Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Total Collected</CardTitle>
              <DollarSign className="h-4 w-4 text-green-600" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-green-600">
                {formatCurrency(collectionSummary?.data?.summary?.total_collected || 0)}
              </div>
              <p className="text-xs text-muted-foreground">This month</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Overdue</CardTitle>
              <AlertCircle className="h-4 w-4 text-red-600" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-red-600">
                {overdueData?.data?.overdue_allocations?.length || 0}
              </div>
              <p className="text-xs text-muted-foreground">Allocations</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Upcoming Due</CardTitle>
              <Clock className="h-4 w-4 text-orange-600" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-orange-600">
                {upcomingData?.data?.upcoming_due?.length || 0}
              </div>
              <p className="text-xs text-muted-foreground">Next 30 days</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Total Payments</CardTitle>
              <Receipt className="h-4 w-4 text-blue-600" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-blue-600">
                {collectionSummary?.data?.summary?.total_payments || 0}
              </div>
              <p className="text-xs text-muted-foreground">This month</p>
            </CardContent>
          </Card>
        </div>

        {/* Tabs */}
        <Tabs value={activeTab} onValueChange={setActiveTab}>
          <TabsList>
            <TabsTrigger value="overview">Overview</TabsTrigger>
            <TabsTrigger value="overdue">Overdue</TabsTrigger>
            <TabsTrigger value="upcoming">Upcoming</TabsTrigger>
            <TabsTrigger value="analytics">Analytics</TabsTrigger>
          </TabsList>

          <TabsContent value="overview" className="mt-6 space-y-6">
            {/* Collection Summary */}
            <Card>
              <CardHeader>
                <CardTitle>Collection Summary</CardTitle>
                <CardDescription>Monthly rent collection breakdown</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                  <div>
                    <p className="text-sm text-gray-600">Rent Amount</p>
                    <p className="text-xl font-bold">
                      {formatCurrency(collectionSummary?.data?.summary?.rent_amount || 0)}
                    </p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-600">GST Amount</p>
                    <p className="text-xl font-bold">
                      {formatCurrency(collectionSummary?.data?.summary?.gst_amount || 0)}
                    </p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-600">Penalties</p>
                    <p className="text-xl font-bold">
                      {formatCurrency(collectionSummary?.data?.summary?.penalty_amount || 0)}
                    </p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-600">Late Fees</p>
                    <p className="text-xl font-bold">
                      {formatCurrency(collectionSummary?.data?.summary?.late_fee_amount || 0)}
                    </p>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Quick Actions */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <Card>
                <CardHeader>
                  <CardTitle className="text-base">Calculate Rent</CardTitle>
                  <CardDescription>Calculate annual, pro-rata, or advance rent</CardDescription>
                </CardHeader>
                <CardContent>
                  <Button className="w-full" onClick={() => setIsCalculateOpen(true)}>
                    <Calculator className="h-4 w-4 mr-2" />
                    Calculate
                  </Button>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle className="text-base">Send Bulk Reminders</CardTitle>
                  <CardDescription>Send reminders to all upcoming dues</CardDescription>
                </CardHeader>
                <CardContent>
                  <Button 
                    className="w-full" 
                    variant="outline"
                    onClick={() => sendBulkRemindersMutation.mutate({
                      reminderType: '30_day_reminder',
                      daysBeforeDue: 30
                    })}
                    disabled={sendBulkRemindersMutation.isPending}
                  >
                    <Send className="h-4 w-4 mr-2" />
                    {sendBulkRemindersMutation.isPending ? 'Sending...' : 'Send 30-Day Reminders'}
                  </Button>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle className="text-base">Download Report</CardTitle>
                  <CardDescription>Export collection report</CardDescription>
                </CardHeader>
                <CardContent>
                  <Button className="w-full" variant="outline">
                    <Download className="h-4 w-4 mr-2" />
                    Download
                  </Button>
                </CardContent>
              </Card>
            </div>
          </TabsContent>

          <TabsContent value="overdue" className="mt-6">
            <Card>
              <CardHeader>
                <div className="flex items-center justify-between">
                  <div>
                    <CardTitle>Overdue Rent</CardTitle>
                    <CardDescription>Allocations with pending rent payments</CardDescription>
                  </div>
                  <Badge className="bg-red-100 text-red-800">
                    {overdueData?.data?.overdue_allocations?.length || 0} Overdue
                  </Badge>
                </div>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {overdueData?.data?.overdue_allocations?.map((allocation: OverdueAllocation) => (
                    <div key={allocation.allocation_id} className="flex items-center justify-between p-4 bg-red-50 rounded-lg border border-red-200">
                      <div className="flex-1">
                        <div className="flex items-center gap-2">
                          <h3 className="font-semibold">{allocation.allocation_number}</h3>
                          <Badge className="bg-red-100 text-red-800">
                            {allocation.days_overdue} days overdue
                          </Badge>
                        </div>
                        <div className="grid grid-cols-3 gap-4 mt-2 text-sm">
                          <div>
                            <p className="text-gray-600">Customer ID</p>
                            <p className="font-medium">{allocation.customer_id}</p>
                          </div>
                          <div>
                            <p className="text-gray-600">Due Date</p>
                            <p className="font-medium">{formatDate(allocation.rent_due_date)}</p>
                          </div>
                          <div>
                            <p className="text-gray-600">Amount Due</p>
                            <p className="font-medium text-red-600">
                              {formatCurrency(allocation.outstanding_rent)}
                            </p>
                          </div>
                        </div>
                      </div>
                      <div className="flex gap-2">
                        <Button 
                          size="sm" 
                          onClick={() => {
                            setSelectedAllocation(allocation.allocation_id)
                            setIsCollectOpen(true)
                          }}
                        >
                          Collect
                        </Button>
                        <Button 
                          size="sm" 
                          variant="outline"
                          onClick={() => {
                            setSelectedAllocation(allocation.allocation_id)
                            setIsReminderOpen(true)
                          }}
                        >
                          <Send className="h-4 w-4" />
                        </Button>
                      </div>
                    </div>
                  ))}
                  {!overdueData?.data?.overdue_allocations?.length && (
                    <p className="text-center text-gray-500 py-8">No overdue allocations</p>
                  )}
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="upcoming" className="mt-6">
            <Card>
              <CardHeader>
                <div className="flex items-center justify-between">
                  <div>
                    <CardTitle>Upcoming Due Dates</CardTitle>
                    <CardDescription>Rent payments due in next 30 days</CardDescription>
                  </div>
                  <Badge className="bg-orange-100 text-orange-800">
                    {upcomingData?.data?.upcoming_due?.length || 0} Upcoming
                  </Badge>
                </div>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {upcomingData?.data?.upcoming_due?.map((due: UpcomingDue) => (
                    <div key={due.allocation_id} className="flex items-center justify-between p-4 bg-orange-50 rounded-lg border border-orange-200">
                      <div className="flex-1">
                        <div className="flex items-center gap-2">
                          <h3 className="font-semibold">{due.allocation_number}</h3>
                          <Badge className="bg-orange-100 text-orange-800">
                            Due in {due.days_until_due} days
                          </Badge>
                          {due.auto_renewal && (
                            <Badge variant="outline">Auto-renewal</Badge>
                          )}
                        </div>
                        <div className="grid grid-cols-3 gap-4 mt-2 text-sm">
                          <div>
                            <p className="text-gray-600">Customer ID</p>
                            <p className="font-medium">{due.customer_id}</p>
                          </div>
                          <div>
                            <p className="text-gray-600">Due Date</p>
                            <p className="font-medium">{formatDate(due.rent_due_date)}</p>
                          </div>
                          <div>
                            <p className="text-gray-600">Annual Rent</p>
                            <p className="font-medium">{formatCurrency(due.annual_rent)}</p>
                          </div>
                        </div>
                      </div>
                      <div className="flex gap-2">
                        <Button 
                          size="sm" 
                          variant="outline"
                          onClick={() => {
                            setSelectedAllocation(due.allocation_id)
                            setIsReminderOpen(true)
                          }}
                        >
                          <Send className="h-4 w-4 mr-2" />
                          Remind
                        </Button>
                      </div>
                    </div>
                  ))}
                  {!upcomingData?.data?.upcoming_due?.length && (
                    <p className="text-center text-gray-500 py-8">No upcoming payments</p>
                  )}
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="analytics" className="mt-6 space-y-6">
            {/* Payment Mode Breakdown */}
            <Card>
              <CardHeader>
                <CardTitle>Payment Mode Distribution</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {collectionSummary?.data?.by_payment_mode && 
                    Object.entries(collectionSummary.data.by_payment_mode).map(([mode, amount]: [string, any]) => (
                      <div key={mode} className="flex items-center justify-between">
                        <span className="text-sm font-medium capitalize">{mode.replace('_', ' ')}</span>
                        <span className="text-sm font-bold">{formatCurrency(amount)}</span>
                      </div>
                    ))
                  }
                </div>
              </CardContent>
            </Card>

            {/* Payment Type Breakdown */}
            <Card>
              <CardHeader>
                <CardTitle>Payment Type Distribution</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {collectionSummary?.data?.by_payment_type && 
                    Object.entries(collectionSummary.data.by_payment_type).map(([type, amount]: [string, any]) => (
                      <div key={type} className="flex items-center justify-between">
                        <span className="text-sm font-medium capitalize">{type.replace('_', ' ')}</span>
                        <span className="text-sm font-bold">{formatCurrency(amount)}</span>
                      </div>
                    ))
                  }
                </div>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>

        {/* Collect Rent Dialog */}
        <Dialog open={isCollectOpen} onOpenChange={setIsCollectOpen}>
          <DialogContent className="max-w-2xl">
            <DialogHeader>
              <DialogTitle>Collect Rent Payment</DialogTitle>
              <DialogDescription>Record a rent payment for the allocation</DialogDescription>
            </DialogHeader>
            <form onSubmit={(e) => {
              e.preventDefault()
              const formData = new FormData(e.currentTarget)
              collectRentMutation.mutate({
                allocationId: selectedAllocation || formData.get('allocation_id'),
                paymentData: {
                  payment_type: formData.get('payment_type'),
                  payment_mode: formData.get('payment_mode'),
                  total_amount: parseFloat(formData.get('total_amount') as string),
                  rent_amount: parseFloat(formData.get('rent_amount') as string),
                  gst_amount: parseFloat(formData.get('gst_amount') as string),
                  period_from: formData.get('period_from'),
                  period_to: formData.get('period_to'),
                  transaction_reference: formData.get('transaction_reference'),
                  remarks: formData.get('remarks')
                }
              })
            }}>
              <div className="grid gap-4 py-4">
                <div>
                  <Label htmlFor="allocation_id">Allocation ID</Label>
                  <Input 
                    id="allocation_id" 
                    name="allocation_id" 
                    defaultValue={selectedAllocation}
                    required 
                  />
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <Label htmlFor="payment_type">Payment Type</Label>
                    <Select name="payment_type" required>
                      <SelectTrigger>
                        <SelectValue placeholder="Select type" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="rent">Rent</SelectItem>
                        <SelectItem value="security_deposit">Security Deposit</SelectItem>
                        <SelectItem value="penalty">Penalty</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  <div>
                    <Label htmlFor="payment_mode">Payment Mode</Label>
                    <Select name="payment_mode" required>
                      <SelectTrigger>
                        <SelectValue placeholder="Select mode" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="cash">Cash</SelectItem>
                        <SelectItem value="cheque">Cheque</SelectItem>
                        <SelectItem value="neft">NEFT</SelectItem>
                        <SelectItem value="rtgs">RTGS</SelectItem>
                        <SelectItem value="upi">UPI</SelectItem>
                        <SelectItem value="auto_debit">Auto Debit</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                </div>

                <div className="grid grid-cols-3 gap-4">
                  <div>
                    <Label htmlFor="rent_amount">Rent Amount</Label>
                    <Input id="rent_amount" name="rent_amount" type="number" step="0.01" required />
                  </div>
                  <div>
                    <Label htmlFor="gst_amount">GST Amount (18%)</Label>
                    <Input id="gst_amount" name="gst_amount" type="number" step="0.01" required />
                  </div>
                  <div>
                    <Label htmlFor="total_amount">Total Amount</Label>
                    <Input id="total_amount" name="total_amount" type="number" step="0.01" required />
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <Label htmlFor="period_from">Period From</Label>
                    <Input id="period_from" name="period_from" type="date" required />
                  </div>
                  <div>
                    <Label htmlFor="period_to">Period To</Label>
                    <Input id="period_to" name="period_to" type="date" required />
                  </div>
                </div>

                <div>
                  <Label htmlFor="transaction_reference">Transaction Reference</Label>
                  <Input id="transaction_reference" name="transaction_reference" />
                </div>

                <div>
                  <Label htmlFor="remarks">Remarks</Label>
                  <Input id="remarks" name="remarks" />
                </div>
              </div>
              <DialogFooter>
                <Button type="button" variant="outline" onClick={() => setIsCollectOpen(false)}>
                  Cancel
                </Button>
                <Button type="submit" disabled={collectRentMutation.isPending}>
                  {collectRentMutation.isPending ? 'Processing...' : 'Collect Payment'}
                </Button>
              </DialogFooter>
            </form>
          </DialogContent>
        </Dialog>

        {/* Calculate Rent Dialog */}
        <Dialog open={isCalculateOpen} onOpenChange={setIsCalculateOpen}>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>Calculate Rent</DialogTitle>
              <DialogDescription>Calculate rent amount for an allocation</DialogDescription>
            </DialogHeader>
            <div className="space-y-4 py-4">
              <div>
                <Label>Calculation Type</Label>
                <Select value={calculationType} onValueChange={(value: any) => setCalculationType(value)}>
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="annual">Annual Rent</SelectItem>
                    <SelectItem value="prorata">Pro-rata Rent</SelectItem>
                    <SelectItem value="advance">Advance Rent</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div>
                <Label htmlFor="calc_allocation_id">Allocation ID</Label>
                <Input id="calc_allocation_id" placeholder="Enter allocation ID" />
              </div>

              {calculationType === 'prorata' && (
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <Label>From Date</Label>
                    <Input type="date" />
                  </div>
                  <div>
                    <Label>To Date</Label>
                    <Input type="date" />
                  </div>
                </div>
              )}

              {calculationType === 'advance' && (
                <div>
                  <Label>Number of Years</Label>
                  <Input type="number" min="1" max="5" defaultValue="1" />
                </div>
              )}
            </div>
            <DialogFooter>
              <Button type="button" variant="outline" onClick={() => setIsCalculateOpen(false)}>
                Cancel
              </Button>
              <Button>Calculate</Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>

        {/* Send Reminder Dialog */}
        <Dialog open={isReminderOpen} onOpenChange={setIsReminderOpen}>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>Send Rent Reminder</DialogTitle>
              <DialogDescription>Send payment reminder to customer</DialogDescription>
            </DialogHeader>
            <form onSubmit={(e) => {
              e.preventDefault()
              const formData = new FormData(e.currentTarget)
              sendReminderMutation.mutate({
                allocationId: selectedAllocation || formData.get('reminder_allocation_id'),
                reminderType: formData.get('reminder_type'),
                daysBeforeDue: parseInt(formData.get('days_before_due') as string)
              })
            }}>
              <div className="grid gap-4 py-4">
                <div>
                  <Label htmlFor="reminder_allocation_id">Allocation ID</Label>
                  <Input 
                    id="reminder_allocation_id" 
                    name="reminder_allocation_id" 
                    defaultValue={selectedAllocation}
                    required 
                  />
                </div>

                <div>
                  <Label htmlFor="reminder_type">Reminder Type</Label>
                  <Select name="reminder_type" required>
                    <SelectTrigger>
                      <SelectValue placeholder="Select type" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="30_day_reminder">30 Days Before Due</SelectItem>
                      <SelectItem value="15_day_reminder">15 Days Before Due</SelectItem>
                      <SelectItem value="7_day_reminder">7 Days Before Due</SelectItem>
                      <SelectItem value="due_date_reminder">Due Date Reminder</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                <div>
                  <Label htmlFor="days_before_due">Days Before Due</Label>
                  <Input id="days_before_due" name="days_before_due" type="number" defaultValue="30" required />
                </div>
              </div>
              <DialogFooter>
                <Button type="button" variant="outline" onClick={() => setIsReminderOpen(false)}>
                  Cancel
                </Button>
                <Button type="submit" disabled={sendReminderMutation.isPending}>
                  {sendReminderMutation.isPending ? 'Sending...' : 'Send Reminder'}
                </Button>
              </DialogFooter>
            </form>
          </DialogContent>
        </Dialog>
      </div>
    </DashboardLayout>
  )
}
