'use client'

import { useState } from 'react'
import { useQuery, useMutation } from '@tanstack/react-query'
import { 
  Send, 
  Mail, 
  MessageSquare,
  Bell,
  Calendar,
  FileText,
  CheckCircle,
  AlertCircle
} from 'lucide-react'
import { DashboardLayout } from '@/components/layout/dashboard-layout'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Textarea } from '@/components/ui/textarea'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Badge } from '@/components/ui/badge'
import { depositService } from '@/services/deposit.service'
import { useToast } from '@/hooks/use-toast'
import { Alert, AlertDescription } from '@/components/ui/alert'

export default function NotificationsPage() {
  const { toast } = useToast()
  const [activeTab, setActiveTab] = useState('send')

  // Send notification state
  const [accountId, setAccountId] = useState('')
  const [notificationType, setNotificationType] = useState('maturity_reminder')
  const [channel, setChannel] = useState<'email' | 'sms' | 'both'>('email')
  const [customMessage, setCustomMessage] = useState('')

  // Maturity reminders state
  const [daysBefore, setDaysBefore] = useState(7)
  const [accountTypes, setAccountTypes] = useState<string[]>([])

  // Fetch notification templates
  const { data: templatesData, isLoading: templatesLoading } = useQuery({
    queryKey: ['notification-templates'],
    queryFn: () => depositService.getNotificationTemplates(),
  })

  // Send notification mutation
  const sendNotificationMutation = useMutation({
    mutationFn: () =>
      depositService.sendNotification({
        account_id: parseInt(accountId),
        notification_type: notificationType,
        channel: channel,
        custom_message: customMessage || undefined,
      }),
    onSuccess: () => {
      toast({
        title: 'Success',
        description: 'Notification sent successfully',
      })
      setAccountId('')
      setCustomMessage('')
    },
    onError: () => {
      toast({
        title: 'Error',
        description: 'Failed to send notification',
        variant: 'destructive',
      })
    },
  })

  // Schedule maturity reminders mutation
  const scheduleRemindersMutation = useMutation({
    mutationFn: () =>
      depositService.scheduleMaturityReminders({
        days_before: daysBefore,
        account_types: accountTypes.length > 0 ? accountTypes : undefined,
      }),
    onSuccess: (data) => {
      toast({
        title: 'Success',
        description: `Maturity reminders scheduled for ${data.data?.accounts_count || 0} accounts`,
      })
    },
    onError: () => {
      toast({
        title: 'Error',
        description: 'Failed to schedule reminders',
        variant: 'destructive',
      })
    },
  })

  const handleSendNotification = () => {
    if (!accountId) {
      toast({
        title: 'Validation Error',
        description: 'Please enter account ID',
        variant: 'destructive',
      })
      return
    }

    sendNotificationMutation.mutate()
  }

  const handleScheduleReminders = () => {
    scheduleRemindersMutation.mutate()
  }

  const notificationTypeOptions = [
    { value: 'maturity_reminder', label: 'Maturity Reminder' },
    { value: 'interest_credit', label: 'Interest Credit Alert' },
    { value: 'low_balance', label: 'Low Balance Alert' },
    { value: 'dormancy_warning', label: 'Dormancy Warning' },
    { value: 'tds_deduction', label: 'TDS Deduction Notice' },
    { value: 'statement_ready', label: 'Statement Ready' },
    { value: 'certificate_ready', label: 'Certificate Ready' },
    { value: 'account_opened', label: 'Account Opened' },
    { value: 'account_closed', label: 'Account Closed' },
    { value: 'custom', label: 'Custom Message' },
  ]

  return (
    <DashboardLayout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Notifications</h1>
            <p className="text-gray-600 mt-1">
              Send notifications and manage alerts for deposit accounts
            </p>
          </div>
        </div>

        {/* Tabs */}
        <Tabs value={activeTab} onValueChange={setActiveTab}>
          <TabsList className="grid w-full grid-cols-3">
            <TabsTrigger value="send">
              <Send className="h-4 w-4 mr-2" />
              Send Notification
            </TabsTrigger>
            <TabsTrigger value="reminders">
              <Calendar className="h-4 w-4 mr-2" />
              Maturity Reminders
            </TabsTrigger>
            <TabsTrigger value="templates">
              <FileText className="h-4 w-4 mr-2" />
              Templates
            </TabsTrigger>
          </TabsList>

          {/* Send Notification Tab */}
          <TabsContent value="send" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle>Send Notification</CardTitle>
                <p className="text-sm text-gray-600 mt-1">
                  Send instant notification to a specific account
                </p>
              </CardHeader>
              <CardContent className="space-y-6">
                <div className="space-y-2">
                  <Label htmlFor="accountId">Account ID or Account Number</Label>
                  <Input
                    id="accountId"
                    placeholder="Enter account ID or number"
                    value={accountId}
                    onChange={(e) => setAccountId(e.target.value)}
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="notificationType">Notification Type</Label>
                  <Select value={notificationType} onValueChange={setNotificationType}>
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      {notificationTypeOptions.map((option) => (
                        <SelectItem key={option.value} value={option.value}>
                          {option.label}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>

                <div className="space-y-2">
                  <Label>Notification Channel</Label>
                  <div className="flex gap-3">
                    <Button
                      variant={channel === 'email' ? 'default' : 'outline'}
                      onClick={() => setChannel('email')}
                      className="flex-1"
                    >
                      <Mail className="h-4 w-4 mr-2" />
                      Email Only
                    </Button>
                    <Button
                      variant={channel === 'sms' ? 'default' : 'outline'}
                      onClick={() => setChannel('sms')}
                      className="flex-1"
                    >
                      <MessageSquare className="h-4 w-4 mr-2" />
                      SMS Only
                    </Button>
                    <Button
                      variant={channel === 'both' ? 'default' : 'outline'}
                      onClick={() => setChannel('both')}
                      className="flex-1"
                    >
                      <Bell className="h-4 w-4 mr-2" />
                      Both
                    </Button>
                  </div>
                </div>

                {notificationType === 'custom' && (
                  <div className="space-y-2">
                    <Label htmlFor="customMessage">Custom Message</Label>
                    <Textarea
                      id="customMessage"
                      placeholder="Enter your custom message..."
                      value={customMessage}
                      onChange={(e) => setCustomMessage(e.target.value)}
                      rows={5}
                    />
                    <p className="text-xs text-gray-500">
                      Use placeholders: {'{customer_name}'}, {'{account_number}'}, {'{balance}'}
                    </p>
                  </div>
                )}

                <Alert className="bg-blue-50 border-blue-200">
                  <AlertCircle className="h-4 w-4 text-blue-600" />
                  <AlertDescription className="text-blue-800">
                    {notificationType === 'custom'
                      ? 'Custom message will be sent with your text'
                      : 'Pre-defined template will be used for this notification type'}
                  </AlertDescription>
                </Alert>

                <Button
                  onClick={handleSendNotification}
                  disabled={sendNotificationMutation.isPending}
                  className="w-full"
                  size="lg"
                >
                  {sendNotificationMutation.isPending ? (
                    <>Sending...</>
                  ) : (
                    <>
                      <Send className="h-5 w-5 mr-2" />
                      Send Notification
                    </>
                  )}
                </Button>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Maturity Reminders Tab */}
          <TabsContent value="reminders" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle>Schedule Maturity Reminders</CardTitle>
                <p className="text-sm text-gray-600 mt-1">
                  Automatically send reminders for accounts nearing maturity
                </p>
              </CardHeader>
              <CardContent className="space-y-6">
                <div className="space-y-2">
                  <Label htmlFor="daysBefore">Send Reminder (Days Before Maturity)</Label>
                  <Select
                    value={daysBefore.toString()}
                    onValueChange={(value) => setDaysBefore(parseInt(value))}
                  >
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="3">3 days before</SelectItem>
                      <SelectItem value="7">7 days before</SelectItem>
                      <SelectItem value="15">15 days before</SelectItem>
                      <SelectItem value="30">30 days before</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                <div className="space-y-2">
                  <Label>Account Types (Leave empty for all)</Label>
                  <div className="space-y-2">
                    <div className="flex items-center space-x-2">
                      <input
                        type="checkbox"
                        id="fd"
                        checked={accountTypes.includes('fd')}
                        onChange={(e) => {
                          if (e.target.checked) {
                            setAccountTypes([...accountTypes, 'fd'])
                          } else {
                            setAccountTypes(accountTypes.filter((t) => t !== 'fd'))
                          }
                        }}
                        className="rounded border-gray-300"
                      />
                      <Label htmlFor="fd" className="cursor-pointer">
                        Fixed Deposits (FD)
                      </Label>
                    </div>
                    <div className="flex items-center space-x-2">
                      <input
                        type="checkbox"
                        id="rd"
                        checked={accountTypes.includes('rd')}
                        onChange={(e) => {
                          if (e.target.checked) {
                            setAccountTypes([...accountTypes, 'rd'])
                          } else {
                            setAccountTypes(accountTypes.filter((t) => t !== 'rd'))
                          }
                        }}
                        className="rounded border-gray-300"
                      />
                      <Label htmlFor="rd" className="cursor-pointer">
                        Recurring Deposits (RD)
                      </Label>
                    </div>
                    <div className="flex items-center space-x-2">
                      <input
                        type="checkbox"
                        id="mis"
                        checked={accountTypes.includes('mis')}
                        onChange={(e) => {
                          if (e.target.checked) {
                            setAccountTypes([...accountTypes, 'mis'])
                          } else {
                            setAccountTypes(accountTypes.filter((t) => t !== 'mis'))
                          }
                        }}
                        className="rounded border-gray-300"
                      />
                      <Label htmlFor="mis" className="cursor-pointer">
                        Monthly Income Scheme (MIS)
                      </Label>
                    </div>
                  </div>
                </div>

                <Alert className="bg-green-50 border-green-200">
                  <CheckCircle className="h-4 w-4 text-green-600" />
                  <AlertDescription className="text-green-800">
                    Reminders will be sent via email and SMS to all eligible accounts. Customers will
                    receive details about their maturity date and amount.
                  </AlertDescription>
                </Alert>

                <Button
                  onClick={handleScheduleReminders}
                  disabled={scheduleRemindersMutation.isPending}
                  className="w-full"
                  size="lg"
                >
                  {scheduleRemindersMutation.isPending ? (
                    <>Scheduling...</>
                  ) : (
                    <>
                      <Calendar className="h-5 w-5 mr-2" />
                      Schedule Maturity Reminders
                    </>
                  )}
                </Button>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Templates Tab */}
          <TabsContent value="templates" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle>Notification Templates</CardTitle>
                <p className="text-sm text-gray-600 mt-1">
                  Pre-defined templates for various notification types
                </p>
              </CardHeader>
              <CardContent>
                {templatesLoading ? (
                  <div className="space-y-4">
                    {[1, 2, 3, 4].map((i) => (
                      <div key={i} className="h-24 bg-gray-100 rounded animate-pulse" />
                    ))}
                  </div>
                ) : (
                  <div className="space-y-4">
                    {templatesData?.data?.templates?.map((template: any) => (
                      <Card key={template.id} className="border-2">
                        <CardContent className="pt-6">
                          <div className="flex items-start justify-between">
                            <div className="flex-1">
                              <div className="flex items-center gap-3 mb-2">
                                <h4 className="font-semibold">{template.name}</h4>
                                <Badge variant="outline">{template.type}</Badge>
                              </div>
                              <p className="text-sm text-gray-600 mb-3">{template.description}</p>
                              <div className="bg-gray-50 p-3 rounded text-sm">
                                <p className="font-medium mb-1">Template:</p>
                                <p className="text-gray-700">{template.content}</p>
                              </div>
                              <div className="flex gap-2 mt-3">
                                <Badge variant="secondary">
                                  <Mail className="h-3 w-3 mr-1" />
                                  {template.email_enabled ? 'Email Enabled' : 'Email Disabled'}
                                </Badge>
                                <Badge variant="secondary">
                                  <MessageSquare className="h-3 w-3 mr-1" />
                                  {template.sms_enabled ? 'SMS Enabled' : 'SMS Disabled'}
                                </Badge>
                              </div>
                            </div>
                            <Button variant="outline" size="sm">
                              Edit
                            </Button>
                          </div>
                        </CardContent>
                      </Card>
                    )) || (
                      <div className="text-center py-12 text-gray-500">
                        <FileText className="h-16 w-16 mx-auto mb-4 opacity-50" />
                        <p className="text-lg font-medium">No templates found</p>
                        <p className="text-sm mt-1">Templates will appear here once configured</p>
                      </div>
                    )}
                  </div>
                )}
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>

        {/* Info Card */}
        <Card className="bg-purple-50 border-purple-200">
          <CardContent className="pt-6">
            <div className="flex gap-3">
              <Bell className="h-5 w-5 text-purple-600 mt-0.5 flex-shrink-0" />
              <div>
                <h3 className="font-semibold text-purple-900">Notification Features</h3>
                <ul className="text-sm text-purple-800 mt-2 space-y-1">
                  <li>• Send instant notifications to specific accounts</li>
                  <li>• Schedule automated maturity reminders</li>
                  <li>• Multi-channel delivery (Email & SMS)</li>
                  <li>• Pre-defined templates for common scenarios</li>
                  <li>• Custom messages with dynamic placeholders</li>
                  <li>• Delivery tracking and confirmation</li>
                </ul>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </DashboardLayout>
  )
}
