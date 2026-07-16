'use client'

import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { 
  Clock, Calendar, Shield, AlertCircle, TrendingUp,
  Users, Settings, FileText, Download, CheckCircle,
  XCircle, Plus
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
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Textarea } from '@/components/ui/textarea'
import { 
  operatingHoursService,
  type FacilityStatus,
  type OperatingHours,
  type SpecialAccessRequest
} from '@/services/locker.service'
import { formatDate, formatTime } from '@/lib/utils'
import { toast } from 'sonner'

export default function OperatingHoursPage() {
  const [isHolidayRequestOpen, setIsHolidayRequestOpen] = useState(false)
  const [isAfterHoursRequestOpen, setIsAfterHoursRequestOpen] = useState(false)
  const [isUpdateHoursOpen, setIsUpdateHoursOpen] = useState(false)
  const [isAddHolidayOpen, setIsAddHolidayOpen] = useState(false)
  const [activeTab, setActiveTab] = useState('status')

  const queryClient = useQueryClient()

  // Queries
  const { data: facilityStatus } = useQuery({
    queryKey: ['facility-status'],
    queryFn: () => operatingHoursService.checkFacilityStatus(),
    refetchInterval: 60000, // Refresh every minute
  })

  const { data: weeklySchedule } = useQuery({
    queryKey: ['weekly-schedule'],
    queryFn: () => operatingHoursService.getWeeklySchedule(),
  })

  const { data: holidays } = useQuery({
    queryKey: ['holidays'],
    queryFn: () => operatingHoursService.getHolidayCalendar(),
  })

  const { data: afterHoursStats } = useQuery({
    queryKey: ['after-hours-stats'],
    queryFn: () => operatingHoursService.getAfterHoursStatistics(),
  })

  const { data: peakHoursAnalysis } = useQuery({
    queryKey: ['peak-hours-analysis'],
    queryFn: () => operatingHoursService.getPeakHoursAnalysis(),
  })

  const { data: emergencyProtocol } = useQuery({
    queryKey: ['emergency-protocol'],
    queryFn: () => operatingHoursService.getEmergencyProtocol(),
  })

  const { data: escortRequirements } = useQuery({
    queryKey: ['escort-requirements'],
    queryFn: () => operatingHoursService.getEscortRequirements(),
  })

  // Mutations
  const requestHolidayAccessMutation = useMutation({
    mutationFn: (data: any) => operatingHoursService.requestHolidayAccess(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['special-access-requests'] })
      setIsHolidayRequestOpen(false)
      toast.success('Holiday access request submitted successfully')
    },
    onError: () => {
      toast.error('Failed to submit holiday access request')
    },
  })

  const requestAfterHoursAccessMutation = useMutation({
    mutationFn: (data: any) => operatingHoursService.requestAfterHoursAccess(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['special-access-requests'] })
      setIsAfterHoursRequestOpen(false)
      toast.success('After-hours access request submitted successfully')
    },
    onError: () => {
      toast.error('Failed to submit after-hours access request')
    },
  })

  const updateOperatingHoursMutation = useMutation({
    mutationFn: (config: any) => operatingHoursService.updateOperatingHours(config),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['weekly-schedule'] })
      setIsUpdateHoursOpen(false)
      toast.success('Operating hours updated successfully')
    },
    onError: () => {
      toast.error('Failed to update operating hours')
    },
  })

  const addHolidayMutation = useMutation({
    mutationFn: ({ date, name, recurring }: { date: string; name: string; recurring: boolean }) =>
      operatingHoursService.addHoliday(date, name, recurring),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['holidays'] })
      setIsAddHolidayOpen(false)
      toast.success('Holiday added successfully')
    },
    onError: () => {
      toast.error('Failed to add holiday')
    },
  })

  return (
    <DashboardLayout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Operating Hours & Access Register</h1>
            <p className="text-gray-600 mt-1">Manage facility hours, special access, and view analytics</p>
          </div>
          <div className="flex gap-2">
            <Button variant="outline" onClick={() => setIsUpdateHoursOpen(true)}>
              <Settings className="h-4 w-4 mr-2" />
              Update Hours
            </Button>
          </div>
        </div>

        {/* Facility Status Banner */}
        <Card className={`border-l-4 ${facilityStatus?.data?.is_open ? 'border-l-green-500 bg-green-50' : 'border-l-red-500 bg-red-50'}`}>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-4">
                <div className={`h-12 w-12 rounded-full flex items-center justify-center ${facilityStatus?.data?.is_open ? 'bg-green-500' : 'bg-red-500'}`}>
                  <Clock className="h-6 w-6 text-white" />
                </div>
                <div>
                  <h3 className="text-xl font-bold">
                    Facility is {facilityStatus?.data?.is_open ? 'Open' : 'Closed'}
                  </h3>
                  <p className="text-sm text-gray-600">
                    Current time: {facilityStatus?.data?.current_time}
                  </p>
                  {!facilityStatus?.data?.is_open && facilityStatus?.data?.next_opening_time && (
                    <p className="text-sm text-gray-600">
                      Opens at: {facilityStatus?.data?.next_opening_time} on {facilityStatus?.data?.next_opening_date}
                    </p>
                  )}
                </div>
              </div>
              {!facilityStatus?.data?.is_open && (
                <Button onClick={() => setIsAfterHoursRequestOpen(true)}>
                  <AlertCircle className="h-4 w-4 mr-2" />
                  Request After-Hours Access
                </Button>
              )}
            </div>
          </CardContent>
        </Card>

        {/* Statistics Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">After-Hours Requests</CardTitle>
              <Clock className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                {afterHoursStats?.data?.total_after_hours_requests || 0}
              </div>
              <p className="text-xs text-muted-foreground">
                {afterHoursStats?.data?.approval_rate?.toFixed(1) || 0}% approved
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Peak Hour</CardTitle>
              <TrendingUp className="h-4 w-4 text-blue-600" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-blue-600">
                {peakHoursAnalysis?.data?.peak_hour || '-'}:00
              </div>
              <p className="text-xs text-muted-foreground">Highest traffic</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Peak Day</CardTitle>
              <Calendar className="h-4 w-4 text-purple-600" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-purple-600">
                {peakHoursAnalysis?.data?.peak_day || '-'}
              </div>
              <p className="text-xs text-muted-foreground">Most busy</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Upcoming Holidays</CardTitle>
              <AlertCircle className="h-4 w-4 text-orange-600" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-orange-600">
                {holidays?.data?.holidays?.length || 0}
              </div>
              <p className="text-xs text-muted-foreground">This year</p>
            </CardContent>
          </Card>
        </div>

        {/* Tabs */}
        <Tabs value={activeTab} onValueChange={setActiveTab}>
          <TabsList>
            <TabsTrigger value="status">Status & Schedule</TabsTrigger>
            <TabsTrigger value="special-access">Special Access</TabsTrigger>
            <TabsTrigger value="analytics">Analytics</TabsTrigger>
            <TabsTrigger value="protocols">Protocols</TabsTrigger>
          </TabsList>

          <TabsContent value="status" className="mt-6 space-y-6">
            {/* Weekly Schedule */}
            <Card>
              <CardHeader>
                <CardTitle>Weekly Operating Hours</CardTitle>
                <CardDescription>Standard locker facility operating schedule</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {weeklySchedule?.data?.weekly_schedule?.map((schedule: OperatingHours) => (
                    <div key={schedule.day} className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                      <div className="flex items-center gap-3">
                        <Calendar className="h-5 w-5 text-gray-600" />
                        <span className="font-medium w-24">{schedule.day}</span>
                      </div>
                      <div className="flex items-center gap-4">
                        {schedule.is_open ? (
                          <>
                            <Badge className="bg-green-100 text-green-800">
                              <CheckCircle className="h-3 w-3 mr-1" />
                              Open
                            </Badge>
                            <span className="text-sm">
                              {schedule.opening_time} - {schedule.closing_time}
                            </span>
                            {schedule.lunch_break_start && (
                              <span className="text-xs text-gray-500">
                                (Lunch: {schedule.lunch_break_start} - {schedule.lunch_break_end})
                              </span>
                            )}
                          </>
                        ) : (
                          <Badge className="bg-red-100 text-red-800">
                            <XCircle className="h-3 w-3 mr-1" />
                            Closed
                          </Badge>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>

            {/* Holiday Calendar */}
            <Card>
              <CardHeader>
                <div className="flex items-center justify-between">
                  <div>
                    <CardTitle>Holiday Calendar</CardTitle>
                    <CardDescription>Scheduled holidays when facility will be closed</CardDescription>
                  </div>
                  <Button onClick={() => setIsAddHolidayOpen(true)}>
                    <Plus className="h-4 w-4 mr-2" />
                    Add Holiday
                  </Button>
                </div>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  {holidays?.data?.holidays?.map((holiday: any) => (
                    <div key={holiday.date} className="flex items-center justify-between p-3 bg-orange-50 rounded-lg">
                      <div className="flex items-center gap-3">
                        <Calendar className="h-5 w-5 text-orange-600" />
                        <div>
                          <p className="font-medium">{holiday.holiday_name}</p>
                          <p className="text-sm text-gray-600">{formatDate(holiday.date)}</p>
                        </div>
                      </div>
                      {holiday.recurring && (
                        <Badge variant="outline">Recurring</Badge>
                      )}
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="special-access" className="mt-6 space-y-6">
            {/* Special Access Requests */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <Card>
                <CardHeader>
                  <CardTitle>Holiday Access</CardTitle>
                  <CardDescription>Request access during holidays</CardDescription>
                </CardHeader>
                <CardContent>
                  <p className="text-sm text-gray-600 mb-4">
                    Prior approval required for locker access on holidays. Submit request at least 48 hours in advance.
                  </p>
                  <Button onClick={() => setIsHolidayRequestOpen(true)} className="w-full">
                    <Calendar className="h-4 w-4 mr-2" />
                    Request Holiday Access
                  </Button>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>After-Hours Access</CardTitle>
                  <CardDescription>Request access outside operating hours</CardDescription>
                </CardHeader>
                <CardContent>
                  <p className="text-sm text-gray-600 mb-4">
                    Special authorization required for after-hours access. Manager approval mandatory.
                  </p>
                  <Button onClick={() => setIsAfterHoursRequestOpen(true)} className="w-full">
                    <Clock className="h-4 w-4 mr-2" />
                    Request After-Hours Access
                  </Button>
                </CardContent>
              </Card>
            </div>

            {/* After-Hours Statistics */}
            <Card>
              <CardHeader>
                <CardTitle>After-Hours Access Statistics</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                  <div>
                    <p className="text-sm text-gray-600">Total Requests</p>
                    <p className="text-2xl font-bold">{afterHoursStats?.data?.total_after_hours_requests || 0}</p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-600">Approved</p>
                    <p className="text-2xl font-bold text-green-600">{afterHoursStats?.data?.approved_requests || 0}</p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-600">Rejected</p>
                    <p className="text-2xl font-bold text-red-600">{afterHoursStats?.data?.rejected_requests || 0}</p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-600">Approval Rate</p>
                    <p className="text-2xl font-bold text-blue-600">
                      {afterHoursStats?.data?.approval_rate?.toFixed(1) || 0}%
                    </p>
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="analytics" className="mt-6 space-y-6">
            {/* Peak Hours Analysis */}
            <Card>
              <CardHeader>
                <CardTitle>Peak Hours Analysis</CardTitle>
                <CardDescription>Access traffic patterns and staffing recommendations</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-6">
                  <div>
                    <h4 className="font-medium mb-3">Hourly Distribution</h4>
                    <div className="space-y-2">
                      {peakHoursAnalysis?.data?.hourly_distribution?.slice(0, 8).map((hour: any) => (
                        <div key={hour.hour} className="flex items-center gap-3">
                          <span className="text-sm w-20">{hour.hour}:00 - {hour.hour + 1}:00</span>
                          <div className="flex-1 bg-gray-200 rounded-full h-6">
                            <div 
                              className="bg-blue-600 h-6 rounded-full flex items-center justify-end pr-2"
                              style={{ width: `${hour.percentage}%` }}
                            >
                              <span className="text-xs text-white font-medium">{hour.count}</span>
                            </div>
                          </div>
                          <span className="text-sm text-gray-600 w-12">{hour.percentage?.toFixed(1)}%</span>
                        </div>
                      ))}
                    </div>
                  </div>

                  <div>
                    <h4 className="font-medium mb-3">Staffing Recommendations</h4>
                    <div className="space-y-2">
                      {peakHoursAnalysis?.data?.recommended_staffing?.map((slot: any, index: number) => (
                        <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                          <div>
                            <p className="font-medium">{slot.time_slot}</p>
                            <p className="text-sm text-gray-600">Avg traffic: {slot.current_average_traffic}</p>
                          </div>
                          <Badge className="bg-blue-100 text-blue-800">
                            <Users className="h-3 w-3 mr-1" />
                            {slot.recommended_staff} staff
                          </Badge>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Daily Distribution */}
            <Card>
              <CardHeader>
                <CardTitle>Daily Traffic Distribution</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  {peakHoursAnalysis?.data?.daily_distribution?.map((day: any) => (
                    <div key={day.day} className="flex items-center gap-3">
                      <span className="text-sm w-24 font-medium">{day.day}</span>
                      <div className="flex-1 bg-gray-200 rounded-full h-8">
                        <div 
                          className="bg-purple-600 h-8 rounded-full flex items-center justify-end pr-3"
                          style={{ width: `${day.percentage}%` }}
                        >
                          <span className="text-sm text-white font-medium">{day.count}</span>
                        </div>
                      </div>
                      <span className="text-sm text-gray-600 w-12">{day.percentage?.toFixed(1)}%</span>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="protocols" className="mt-6 space-y-6">
            {/* Emergency Access Protocol */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Shield className="h-5 w-5 text-red-600" />
                  Emergency Access Protocol
                </CardTitle>
                <CardDescription>Requirements for emergency locker access</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div className="grid grid-cols-2 gap-4">
                    <div className="flex items-start gap-3">
                      {emergencyProtocol?.data?.requires_manager_approval ? (
                        <CheckCircle className="h-5 w-5 text-green-600 mt-0.5" />
                      ) : (
                        <XCircle className="h-5 w-5 text-gray-400 mt-0.5" />
                      )}
                      <div>
                        <p className="font-medium">Manager Approval</p>
                        <p className="text-sm text-gray-600">Required for authorization</p>
                      </div>
                    </div>
                    <div className="flex items-start gap-3">
                      {emergencyProtocol?.data?.requires_security_officer ? (
                        <CheckCircle className="h-5 w-5 text-green-600 mt-0.5" />
                      ) : (
                        <XCircle className="h-5 w-5 text-gray-400 mt-0.5" />
                      )}
                      <div>
                        <p className="font-medium">Security Officer</p>
                        <p className="text-sm text-gray-600">Must be present</p>
                      </div>
                    </div>
                    <div className="flex items-start gap-3">
                      {emergencyProtocol?.data?.requires_dual_authentication ? (
                        <CheckCircle className="h-5 w-5 text-green-600 mt-0.5" />
                      ) : (
                        <XCircle className="h-5 w-5 text-gray-400 mt-0.5" />
                      )}
                      <div>
                        <p className="font-medium">Dual Authentication</p>
                        <p className="text-sm text-gray-600">Two-factor verification</p>
                      </div>
                    </div>
                    <div className="flex items-start gap-3">
                      {emergencyProtocol?.data?.incident_report_required ? (
                        <CheckCircle className="h-5 w-5 text-green-600 mt-0.5" />
                      ) : (
                        <XCircle className="h-5 w-5 text-gray-400 mt-0.5" />
                      )}
                      <div>
                        <p className="font-medium">Incident Report</p>
                        <p className="text-sm text-gray-600">Documentation mandatory</p>
                      </div>
                    </div>
                  </div>

                  {emergencyProtocol?.data?.special_procedures && (
                    <div className="mt-4">
                      <h4 className="font-medium mb-2">Special Procedures:</h4>
                      <ul className="list-disc list-inside space-y-1 text-sm text-gray-600">
                        {emergencyProtocol.data.special_procedures.map((procedure: string, index: number) => (
                          <li key={index}>{procedure}</li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>

            {/* Escort Requirements */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Users className="h-5 w-5 text-blue-600" />
                  Escort Service Requirements
                </CardTitle>
                <CardDescription>Bank official accompaniment rules</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div>
                    <h4 className="font-medium mb-2">Escort Required For:</h4>
                    <div className="space-y-2">
                      {escortRequirements?.data?.escort_mandatory_for?.map((category: string, index: number) => (
                        <Badge key={index} variant="outline" className="mr-2">
                          {category}
                        </Badge>
                      ))}
                    </div>
                  </div>

                  <div>
                    <h4 className="font-medium mb-2">Minimum Designation:</h4>
                    <Badge className="bg-blue-100 text-blue-800">
                      {escortRequirements?.data?.minimum_designation || 'Assistant Manager'}
                    </Badge>
                  </div>

                  {escortRequirements?.data?.escort_responsibilities && (
                    <div>
                      <h4 className="font-medium mb-2">Escort Responsibilities:</h4>
                      <ul className="list-disc list-inside space-y-1 text-sm text-gray-600">
                        {escortRequirements.data.escort_responsibilities.map((responsibility: string, index: number) => (
                          <li key={index}>{responsibility}</li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>

        {/* Holiday Access Request Dialog */}
        <Dialog open={isHolidayRequestOpen} onOpenChange={setIsHolidayRequestOpen}>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>Request Holiday Access</DialogTitle>
              <DialogDescription>
                Submit a request for locker access during a holiday
              </DialogDescription>
            </DialogHeader>
            <form onSubmit={(e) => {
              e.preventDefault()
              const formData = new FormData(e.currentTarget)
              requestHolidayAccessMutation.mutate({
                customer_id: formData.get('customer_id'),
                locker_id: formData.get('locker_id'),
                allocation_id: formData.get('allocation_id'),
                access_date: formData.get('access_date'),
                reason: formData.get('reason'),
              })
            }}>
              <div className="grid gap-4 py-4">
                <div>
                  <Label htmlFor="customer_id">Customer ID</Label>
                  <Input id="customer_id" name="customer_id" required />
                </div>
                <div>
                  <Label htmlFor="locker_id">Locker ID</Label>
                  <Input id="locker_id" name="locker_id" required />
                </div>
                <div>
                  <Label htmlFor="allocation_id">Allocation ID</Label>
                  <Input id="allocation_id" name="allocation_id" required />
                </div>
                <div>
                  <Label htmlFor="access_date">Holiday Date</Label>
                  <Input id="access_date" name="access_date" type="date" required />
                </div>
                <div>
                  <Label htmlFor="reason">Reason for Access</Label>
                  <Textarea id="reason" name="reason" rows={3} required />
                </div>
              </div>
              <DialogFooter>
                <Button type="button" variant="outline" onClick={() => setIsHolidayRequestOpen(false)}>
                  Cancel
                </Button>
                <Button type="submit" disabled={requestHolidayAccessMutation.isPending}>
                  {requestHolidayAccessMutation.isPending ? 'Submitting...' : 'Submit Request'}
                </Button>
              </DialogFooter>
            </form>
          </DialogContent>
        </Dialog>

        {/* After-Hours Access Request Dialog */}
        <Dialog open={isAfterHoursRequestOpen} onOpenChange={setIsAfterHoursRequestOpen}>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>Request After-Hours Access</DialogTitle>
              <DialogDescription>
                Submit a request for locker access outside operating hours
              </DialogDescription>
            </DialogHeader>
            <form onSubmit={(e) => {
              e.preventDefault()
              const formData = new FormData(e.currentTarget)
              requestAfterHoursAccessMutation.mutate({
                customer_id: formData.get('customer_id'),
                locker_id: formData.get('locker_id'),
                allocation_id: formData.get('allocation_id'),
                access_date: formData.get('access_date'),
                access_time: formData.get('access_time'),
                reason: formData.get('reason'),
              })
            }}>
              <div className="grid gap-4 py-4">
                <div>
                  <Label htmlFor="customer_id">Customer ID</Label>
                  <Input id="customer_id" name="customer_id" required />
                </div>
                <div>
                  <Label htmlFor="locker_id">Locker ID</Label>
                  <Input id="locker_id" name="locker_id" required />
                </div>
                <div>
                  <Label htmlFor="allocation_id">Allocation ID</Label>
                  <Input id="allocation_id" name="allocation_id" required />
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <Label htmlFor="access_date">Access Date</Label>
                    <Input id="access_date" name="access_date" type="date" required />
                  </div>
                  <div>
                    <Label htmlFor="access_time">Access Time</Label>
                    <Input id="access_time" name="access_time" type="time" required />
                  </div>
                </div>
                <div>
                  <Label htmlFor="reason">Reason for Access</Label>
                  <Textarea id="reason" name="reason" rows={3} required />
                </div>
              </div>
              <DialogFooter>
                <Button type="button" variant="outline" onClick={() => setIsAfterHoursRequestOpen(false)}>
                  Cancel
                </Button>
                <Button type="submit" disabled={requestAfterHoursAccessMutation.isPending}>
                  {requestAfterHoursAccessMutation.isPending ? 'Submitting...' : 'Submit Request'}
                </Button>
              </DialogFooter>
            </form>
          </DialogContent>
        </Dialog>

        {/* Update Operating Hours Dialog */}
        <Dialog open={isUpdateHoursOpen} onOpenChange={setIsUpdateHoursOpen}>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>Update Operating Hours</DialogTitle>
              <DialogDescription>
                Modify facility operating hours configuration
              </DialogDescription>
            </DialogHeader>
            <form onSubmit={(e) => {
              e.preventDefault()
              const formData = new FormData(e.currentTarget)
              updateOperatingHoursMutation.mutate({
                weekday_start: formData.get('weekday_start') || undefined,
                weekday_end: formData.get('weekday_end') || undefined,
                saturday_start: formData.get('saturday_start') || undefined,
                saturday_end: formData.get('saturday_end') || undefined,
                lunch_start: formData.get('lunch_start') || undefined,
                lunch_end: formData.get('lunch_end') || undefined,
              })
            }}>
              <div className="grid gap-4 py-4">
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <Label htmlFor="weekday_start">Weekday Start</Label>
                    <Input id="weekday_start" name="weekday_start" type="time" defaultValue="10:00" />
                  </div>
                  <div>
                    <Label htmlFor="weekday_end">Weekday End</Label>
                    <Input id="weekday_end" name="weekday_end" type="time" defaultValue="16:00" />
                  </div>
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <Label htmlFor="saturday_start">Saturday Start</Label>
                    <Input id="saturday_start" name="saturday_start" type="time" defaultValue="10:00" />
                  </div>
                  <div>
                    <Label htmlFor="saturday_end">Saturday End</Label>
                    <Input id="saturday_end" name="saturday_end" type="time" defaultValue="13:00" />
                  </div>
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <Label htmlFor="lunch_start">Lunch Break Start</Label>
                    <Input id="lunch_start" name="lunch_start" type="time" />
                  </div>
                  <div>
                    <Label htmlFor="lunch_end">Lunch Break End</Label>
                    <Input id="lunch_end" name="lunch_end" type="time" />
                  </div>
                </div>
              </div>
              <DialogFooter>
                <Button type="button" variant="outline" onClick={() => setIsUpdateHoursOpen(false)}>
                  Cancel
                </Button>
                <Button type="submit" disabled={updateOperatingHoursMutation.isPending}>
                  {updateOperatingHoursMutation.isPending ? 'Updating...' : 'Update Hours'}
                </Button>
              </DialogFooter>
            </form>
          </DialogContent>
        </Dialog>

        {/* Add Holiday Dialog */}
        <Dialog open={isAddHolidayOpen} onOpenChange={setIsAddHolidayOpen}>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>Add Holiday</DialogTitle>
              <DialogDescription>
                Add a new holiday to the calendar
              </DialogDescription>
            </DialogHeader>
            <form onSubmit={(e) => {
              e.preventDefault()
              const formData = new FormData(e.currentTarget)
              addHolidayMutation.mutate({
                date: formData.get('holiday_date') as string,
                name: formData.get('holiday_name') as string,
                recurring: formData.get('recurring') === 'on',
              })
            }}>
              <div className="grid gap-4 py-4">
                <div>
                  <Label htmlFor="holiday_date">Holiday Date</Label>
                  <Input id="holiday_date" name="holiday_date" type="date" required />
                </div>
                <div>
                  <Label htmlFor="holiday_name">Holiday Name</Label>
                  <Input id="holiday_name" name="holiday_name" required placeholder="e.g., Independence Day" />
                </div>
                <div className="flex items-center gap-2">
                  <input type="checkbox" id="recurring" name="recurring" className="h-4 w-4" />
                  <Label htmlFor="recurring" className="cursor-pointer">
                    Recurring annually
                  </Label>
                </div>
              </div>
              <DialogFooter>
                <Button type="button" variant="outline" onClick={() => setIsAddHolidayOpen(false)}>
                  Cancel
                </Button>
                <Button type="submit" disabled={addHolidayMutation.isPending}>
                  {addHolidayMutation.isPending ? 'Adding...' : 'Add Holiday'}
                </Button>
              </DialogFooter>
            </form>
          </DialogContent>
        </Dialog>
      </div>
    </DashboardLayout>
  )
}
