'use client'

import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Bell, Mail, MessageSquare, Save, Settings } from 'lucide-react'
import { DashboardLayout } from '@/components/layout/dashboard-layout'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card'
import { Switch } from '@/components/ui/switch'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { useToast } from '@/components/ui/use-toast'
import { notificationService } from '@/services/notification.service'

export default function NotificationSettingsPage() {
  const { toast } = useToast()
  const queryClient = useQueryClient()

  const { data, isLoading } = useQuery({
    queryKey: ['notification-preferences'],
    queryFn: () => notificationService.getPreferences(),
  })

  const preferences = data?.data?.data

  const [formData, setFormData] = useState({
    rent_due_reminder_enabled: true,
    lease_expiry_alert_enabled: true,
    payment_received_enabled: true,
    maintenance_update_enabled: true,
    utility_bill_due_enabled: true,
    payment_overdue_enabled: true,
    email_enabled: true,
    sms_enabled: false,
    email_address: '',
    phone_number: '',
  })

  // Update form when data loads
  useState(() => {
    if (preferences) {
      setFormData({
        rent_due_reminder_enabled: preferences.rent_due_reminder_enabled,
        lease_expiry_alert_enabled: preferences.lease_expiry_alert_enabled,
        payment_received_enabled: preferences.payment_received_enabled,
        maintenance_update_enabled: preferences.maintenance_update_enabled,
        utility_bill_due_enabled: preferences.utility_bill_due_enabled,
        payment_overdue_enabled: preferences.payment_overdue_enabled,
        email_enabled: preferences.email_enabled,
        sms_enabled: preferences.sms_enabled,
        email_address: preferences.email_address || '',
        phone_number: preferences.phone_number || '',
      })
    }
  })

  const updateMutation = useMutation({
    mutationFn: (data: any) => notificationService.updatePreferences(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['notification-preferences'] })
      toast({
        title: 'Success',
        description: 'Notification preferences updated successfully',
      })
    },
    onError: (error: any) => {
      toast({
        title: 'Error',
        description: error.response?.data?.error?.message || 'Failed to update preferences',
        variant: 'destructive',
      })
    },
  })

  const handleSave = () => {
    updateMutation.mutate(formData)
  }

  if (isLoading) {
    return (
      <DashboardLayout>
        <div className="flex items-center justify-center h-64">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
        </div>
      </DashboardLayout>
    )
  }

  return (
    <DashboardLayout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Notification Settings</h1>
            <p className="text-gray-600 mt-1">Manage your notification preferences and channels</p>
          </div>
          <Button onClick={handleSave} disabled={updateMutation.isPending}>
            <Save className="h-4 w-4 mr-2" />
            {updateMutation.isPending ? 'Saving...' : 'Save Changes'}
          </Button>
        </div>

        {/* Notification Channels */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Settings className="h-5 w-5" />
              Notification Channels
            </CardTitle>
            <CardDescription>Choose how you want to receive notifications</CardDescription>
          </CardHeader>
          <CardContent className="space-y-6">
            {/* Email Channel */}
            <div className="flex items-start justify-between p-4 border rounded-lg">
              <div className="flex items-start gap-3">
                <Mail className="h-5 w-5 text-blue-600 mt-1" />
                <div>
                  <h3 className="font-semibold">Email Notifications</h3>
                  <p className="text-sm text-gray-600 mt-1">
                    Receive notifications via email
                  </p>
                  {formData.email_enabled && (
                    <div className="mt-3">
                      <Label htmlFor="email_address">Email Address</Label>
                      <Input
                        id="email_address"
                        type="email"
                        placeholder="your@email.com"
                        value={formData.email_address}
                        onChange={(e) => setFormData({ ...formData, email_address: e.target.value })}
                        className="mt-1"
                      />
                    </div>
                  )}
                </div>
              </div>
              <Switch
                checked={formData.email_enabled}
                onCheckedChange={(checked) => setFormData({ ...formData, email_enabled: checked })}
              />
            </div>

            {/* SMS Channel */}
            <div className="flex items-start justify-between p-4 border rounded-lg">
              <div className="flex items-start gap-3">
                <MessageSquare className="h-5 w-5 text-green-600 mt-1" />
                <div>
                  <h3 className="font-semibold">SMS Notifications</h3>
                  <p className="text-sm text-gray-600 mt-1">
                    Receive notifications via SMS
                  </p>
                  {formData.sms_enabled && (
                    <div className="mt-3">
                      <Label htmlFor="phone_number">Phone Number</Label>
                      <Input
                        id="phone_number"
                        type="tel"
                        placeholder="+91 9876543210"
                        value={formData.phone_number}
                        onChange={(e) => setFormData({ ...formData, phone_number: e.target.value })}
                        className="mt-1"
                      />
                    </div>
                  )}
                </div>
              </div>
              <Switch
                checked={formData.sms_enabled}
                onCheckedChange={(checked) => setFormData({ ...formData, sms_enabled: checked })}
              />
            </div>
          </CardContent>
        </Card>

        {/* Notification Types */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Bell className="h-5 w-5" />
              Notification Types
            </CardTitle>
            <CardDescription>Choose which notifications you want to receive</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <NotificationToggle
              label="Rent Due Reminders"
              description="Get notified 3 days before rent is due"
              checked={formData.rent_due_reminder_enabled}
              onChange={(checked) => setFormData({ ...formData, rent_due_reminder_enabled: checked })}
            />

            <NotificationToggle
              label="Lease Expiry Alerts"
              description="Get notified 60 days before lease expires"
              checked={formData.lease_expiry_alert_enabled}
              onChange={(checked) => setFormData({ ...formData, lease_expiry_alert_enabled: checked })}
            />

            <NotificationToggle
              label="Payment Received"
              description="Get notified when rent payment is received"
              checked={formData.payment_received_enabled}
              onChange={(checked) => setFormData({ ...formData, payment_received_enabled: checked })}
            />

            <NotificationToggle
              label="Maintenance Updates"
              description="Get notified about maintenance request updates"
              checked={formData.maintenance_update_enabled}
              onChange={(checked) => setFormData({ ...formData, maintenance_update_enabled: checked })}
            />

            <NotificationToggle
              label="Utility Bill Due"
              description="Get notified when utility bills are due"
              checked={formData.utility_bill_due_enabled}
              onChange={(checked) => setFormData({ ...formData, utility_bill_due_enabled: checked })}
            />

            <NotificationToggle
              label="Payment Overdue"
              description="Get notified about overdue rent payments"
              checked={formData.payment_overdue_enabled}
              onChange={(checked) => setFormData({ ...formData, payment_overdue_enabled: checked })}
            />
          </CardContent>
        </Card>
      </div>
    </DashboardLayout>
  )
}

function NotificationToggle({
  label,
  description,
  checked,
  onChange,
}: {
  label: string
  description: string
  checked: boolean
  onChange: (checked: boolean) => void
}) {
  return (
    <div className="flex items-center justify-between p-4 border rounded-lg hover:bg-gray-50 transition-colors">
      <div>
        <h4 className="font-medium">{label}</h4>
        <p className="text-sm text-gray-600 mt-1">{description}</p>
      </div>
      <Switch checked={checked} onCheckedChange={onChange} />
    </div>
  )
}
