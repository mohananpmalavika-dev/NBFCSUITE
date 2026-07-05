'use client'

import { useState } from 'react'
import { useQuery, useMutation } from '@tanstack/react-query'
import { Save, User, Bell, Lock, Building, Palette } from 'lucide-react'
import { DashboardLayout } from '@/components/layout/dashboard-layout'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { useToast } from '@/hooks/use-toast'
import { useAuth } from '@/contexts/auth-context'

export default function SettingsPage() {
  const { user } = useAuth()
  const { toast } = useToast()

  return (
    <DashboardLayout>
      <div className="space-y-6">
        {/* Header */}
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Settings</h1>
          <p className="text-gray-600 mt-1">Manage your account and application preferences</p>
        </div>

        {/* Settings Tabs */}
        <Tabs defaultValue="profile" className="space-y-6">
          <TabsList>
            <TabsTrigger value="profile">
              <User className="h-4 w-4 mr-2" />
              Profile
            </TabsTrigger>
            <TabsTrigger value="security">
              <Lock className="h-4 w-4 mr-2" />
              Security
            </TabsTrigger>
            <TabsTrigger value="notifications">
              <Bell className="h-4 w-4 mr-2" />
              Notifications
            </TabsTrigger>
            <TabsTrigger value="organization">
              <Building className="h-4 w-4 mr-2" />
              Organization
            </TabsTrigger>
            <TabsTrigger value="appearance">
              <Palette className="h-4 w-4 mr-2" />
              Appearance
            </TabsTrigger>
          </TabsList>

          {/* Profile Settings */}
          <TabsContent value="profile">
            <ProfileSettings user={user} />
          </TabsContent>

          {/* Security Settings */}
          <TabsContent value="security">
            <SecuritySettings />
          </TabsContent>

          {/* Notification Settings */}
          <TabsContent value="notifications">
            <NotificationSettings />
          </TabsContent>

          {/* Organization Settings */}
          <TabsContent value="organization">
            <OrganizationSettings />
          </TabsContent>

          {/* Appearance Settings */}
          <TabsContent value="appearance">
            <AppearanceSettings />
          </TabsContent>
        </Tabs>
      </div>
    </DashboardLayout>
  )
}

function ProfileSettings({ user }: { user: any }) {
  const { toast } = useToast()
  const [formData, setFormData] = useState({
    full_name: user?.full_name || '',
    email: user?.email || '',
    username: user?.username || '',
    phone: '',
  })

  const handleSave = () => {
    toast({
      title: 'Profile updated',
      description: 'Your profile has been updated successfully',
    })
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Profile Information</CardTitle>
      </CardHeader>
      <CardContent className="space-y-6">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="space-y-2">
            <Label htmlFor="full_name">Full Name</Label>
            <Input
              id="full_name"
              value={formData.full_name}
              onChange={(e) => setFormData({ ...formData, full_name: e.target.value })}
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="username">Username</Label>
            <Input
              id="username"
              value={formData.username}
              onChange={(e) => setFormData({ ...formData, username: e.target.value })}
              disabled
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="email">Email</Label>
            <Input
              id="email"
              type="email"
              value={formData.email}
              onChange={(e) => setFormData({ ...formData, email: e.target.value })}
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="phone">Phone Number</Label>
            <Input
              id="phone"
              type="tel"
              value={formData.phone}
              onChange={(e) => setFormData({ ...formData, phone: e.target.value })}
            />
          </div>
        </div>

        <div className="space-y-2">
          <Label htmlFor="role">Role</Label>
          <Input
            id="role"
            value={user?.role || ''}
            disabled
          />
          <p className="text-sm text-gray-500">Contact your administrator to change your role</p>
        </div>

        <div className="flex justify-end">
          <Button onClick={handleSave}>
            <Save className="h-4 w-4 mr-2" />
            Save Changes
          </Button>
        </div>
      </CardContent>
    </Card>
  )
}

function SecuritySettings() {
  const { toast } = useToast()
  const [passwords, setPasswords] = useState({
    current: '',
    new: '',
    confirm: '',
  })

  const handleChangePassword = () => {
    if (passwords.new !== passwords.confirm) {
      toast({
        title: 'Error',
        description: 'New passwords do not match',
        variant: 'destructive',
      })
      return
    }

    toast({
      title: 'Password changed',
      description: 'Your password has been changed successfully',
    })
    setPasswords({ current: '', new: '', confirm: '' })
  }

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle>Change Password</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="current_password">Current Password</Label>
            <Input
              id="current_password"
              type="password"
              value={passwords.current}
              onChange={(e) => setPasswords({ ...passwords, current: e.target.value })}
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="new_password">New Password</Label>
            <Input
              id="new_password"
              type="password"
              value={passwords.new}
              onChange={(e) => setPasswords({ ...passwords, new: e.target.value })}
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="confirm_password">Confirm New Password</Label>
            <Input
              id="confirm_password"
              type="password"
              value={passwords.confirm}
              onChange={(e) => setPasswords({ ...passwords, confirm: e.target.value })}
            />
          </div>

          <div className="flex justify-end">
            <Button onClick={handleChangePassword}>
              <Lock className="h-4 w-4 mr-2" />
              Change Password
            </Button>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Two-Factor Authentication</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <p className="text-sm text-gray-600">
            Add an extra layer of security to your account by enabling two-factor authentication.
          </p>
          <Button variant="outline">Enable 2FA</Button>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Active Sessions</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-3">
            <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
              <div>
                <p className="font-medium">Current Session</p>
                <p className="text-sm text-gray-600">Windows • Chrome • India</p>
              </div>
              <span className="text-sm text-green-600 font-medium">Active</span>
            </div>
          </div>
          <Button variant="outline" className="w-full">Logout All Other Sessions</Button>
        </CardContent>
      </Card>
    </div>
  )
}

function NotificationSettings() {
  const { toast } = useToast()
  const [settings, setSettings] = useState({
    emailNotifications: true,
    smsNotifications: false,
    whatsappNotifications: false,
    loanApproval: true,
    paymentReminders: true,
    systemAlerts: true,
    marketingEmails: false,
  })

  const handleSave = () => {
    toast({
      title: 'Settings saved',
      description: 'Your notification preferences have been saved',
    })
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Notification Preferences</CardTitle>
      </CardHeader>
      <CardContent className="space-y-6">
        <div className="space-y-4">
          <h3 className="font-semibold">Notification Channels</h3>
          
          <div className="flex items-center justify-between">
            <div>
              <p className="font-medium">Email Notifications</p>
              <p className="text-sm text-gray-600">Receive notifications via email</p>
            </div>
            <input
              type="checkbox"
              checked={settings.emailNotifications}
              onChange={(e) => setSettings({ ...settings, emailNotifications: e.target.checked })}
              className="h-4 w-4"
            />
          </div>

          <div className="flex items-center justify-between">
            <div>
              <p className="font-medium">SMS Notifications</p>
              <p className="text-sm text-gray-600">Receive notifications via SMS</p>
            </div>
            <input
              type="checkbox"
              checked={settings.smsNotifications}
              onChange={(e) => setSettings({ ...settings, smsNotifications: e.target.checked })}
              className="h-4 w-4"
            />
          </div>

          <div className="flex items-center justify-between">
            <div>
              <p className="font-medium">WhatsApp Notifications</p>
              <p className="text-sm text-gray-600">Receive notifications via WhatsApp</p>
            </div>
            <input
              type="checkbox"
              checked={settings.whatsappNotifications}
              onChange={(e) => setSettings({ ...settings, whatsappNotifications: e.target.checked })}
              className="h-4 w-4"
            />
          </div>
        </div>

        <div className="border-t pt-6 space-y-4">
          <h3 className="font-semibold">Notification Types</h3>
          
          <div className="flex items-center justify-between">
            <div>
              <p className="font-medium">Loan Approvals</p>
              <p className="text-sm text-gray-600">Get notified about loan approval activities</p>
            </div>
            <input
              type="checkbox"
              checked={settings.loanApproval}
              onChange={(e) => setSettings({ ...settings, loanApproval: e.target.checked })}
              className="h-4 w-4"
            />
          </div>

          <div className="flex items-center justify-between">
            <div>
              <p className="font-medium">Payment Reminders</p>
              <p className="text-sm text-gray-600">Receive reminders for upcoming payments</p>
            </div>
            <input
              type="checkbox"
              checked={settings.paymentReminders}
              onChange={(e) => setSettings({ ...settings, paymentReminders: e.target.checked })}
              className="h-4 w-4"
            />
          </div>

          <div className="flex items-center justify-between">
            <div>
              <p className="font-medium">System Alerts</p>
              <p className="text-sm text-gray-600">Important system notifications and alerts</p>
            </div>
            <input
              type="checkbox"
              checked={settings.systemAlerts}
              onChange={(e) => setSettings({ ...settings, systemAlerts: e.target.checked })}
              className="h-4 w-4"
            />
          </div>

          <div className="flex items-center justify-between">
            <div>
              <p className="font-medium">Marketing Emails</p>
              <p className="text-sm text-gray-600">Updates about new features and offers</p>
            </div>
            <input
              type="checkbox"
              checked={settings.marketingEmails}
              onChange={(e) => setSettings({ ...settings, marketingEmails: e.target.checked })}
              className="h-4 w-4"
            />
          </div>
        </div>

        <div className="flex justify-end pt-4">
          <Button onClick={handleSave}>
            <Save className="h-4 w-4 mr-2" />
            Save Preferences
          </Button>
        </div>
      </CardContent>
    </Card>
  )
}

function OrganizationSettings() {
  const { toast } = useToast()
  const [orgData, setOrgData] = useState({
    name: 'NBFC Company Ltd',
    code: 'NBFC001',
    address: '123 Business Street',
    city: 'Mumbai',
    state: 'Maharashtra',
    pincode: '400001',
    phone: '+91 22 1234 5678',
    email: 'info@nbfc.com',
    gst: 'GST123456789',
    pan: 'PANXXX1234X',
  })

  const handleSave = () => {
    toast({
      title: 'Organization updated',
      description: 'Organization details have been updated successfully',
    })
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Organization Details</CardTitle>
      </CardHeader>
      <CardContent className="space-y-6">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="space-y-2">
            <Label htmlFor="org_name">Organization Name</Label>
            <Input
              id="org_name"
              value={orgData.name}
              onChange={(e) => setOrgData({ ...orgData, name: e.target.value })}
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="org_code">Organization Code</Label>
            <Input
              id="org_code"
              value={orgData.code}
              onChange={(e) => setOrgData({ ...orgData, code: e.target.value })}
              disabled
            />
          </div>

          <div className="md:col-span-2 space-y-2">
            <Label htmlFor="address">Address</Label>
            <Input
              id="address"
              value={orgData.address}
              onChange={(e) => setOrgData({ ...orgData, address: e.target.value })}
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="city">City</Label>
            <Input
              id="city"
              value={orgData.city}
              onChange={(e) => setOrgData({ ...orgData, city: e.target.value })}
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="state">State</Label>
            <Input
              id="state"
              value={orgData.state}
              onChange={(e) => setOrgData({ ...orgData, state: e.target.value })}
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="pincode">Pincode</Label>
            <Input
              id="pincode"
              value={orgData.pincode}
              onChange={(e) => setOrgData({ ...orgData, pincode: e.target.value })}
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="phone">Phone</Label>
            <Input
              id="phone"
              value={orgData.phone}
              onChange={(e) => setOrgData({ ...orgData, phone: e.target.value })}
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="org_email">Email</Label>
            <Input
              id="org_email"
              type="email"
              value={orgData.email}
              onChange={(e) => setOrgData({ ...orgData, email: e.target.value })}
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="gst">GST Number</Label>
            <Input
              id="gst"
              value={orgData.gst}
              onChange={(e) => setOrgData({ ...orgData, gst: e.target.value })}
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="pan">PAN Number</Label>
            <Input
              id="pan"
              value={orgData.pan}
              onChange={(e) => setOrgData({ ...orgData, pan: e.target.value })}
            />
          </div>
        </div>

        <div className="flex justify-end">
          <Button onClick={handleSave}>
            <Save className="h-4 w-4 mr-2" />
            Save Changes
          </Button>
        </div>
      </CardContent>
    </Card>
  )
}

function AppearanceSettings() {
  const { toast } = useToast()
  const [theme, setTheme] = useState('light')
  const [language, setLanguage] = useState('en')

  const handleSave = () => {
    toast({
      title: 'Preferences saved',
      description: 'Your appearance preferences have been saved',
    })
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Appearance Preferences</CardTitle>
      </CardHeader>
      <CardContent className="space-y-6">
        <div className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="theme">Theme</Label>
            <select
              id="theme"
              value={theme}
              onChange={(e) => setTheme(e.target.value)}
              className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
            >
              <option value="light">Light</option>
              <option value="dark">Dark</option>
              <option value="system">System</option>
            </select>
            <p className="text-sm text-gray-500">Choose your preferred theme</p>
          </div>

          <div className="space-y-2">
            <Label htmlFor="language">Language</Label>
            <select
              id="language"
              value={language}
              onChange={(e) => setLanguage(e.target.value)}
              className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
            >
              <option value="en">English</option>
              <option value="hi">Hindi</option>
              <option value="mr">Marathi</option>
            </select>
            <p className="text-sm text-gray-500">Select your preferred language</p>
          </div>
        </div>

        <div className="flex justify-end">
          <Button onClick={handleSave}>
            <Save className="h-4 w-4 mr-2" />
            Save Preferences
          </Button>
        </div>
      </CardContent>
    </Card>
  )
}
