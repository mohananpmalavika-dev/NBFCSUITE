'use client'

import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { 
  Plus, Search, Filter, Eye, Clock, CheckCircle, XCircle,
  User, UserCheck, Fingerprint, Camera, PenTool, Shield,
  AlertTriangle, LogOut, FileText, Download
} from 'lucide-react'
import { DashboardLayout } from '@/components/layout/dashboard-layout'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Badge } from '@/components/ui/badge'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
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
  accessService, 
  AccessorType, 
  AccessPurpose, 
  type LockerAccessLog 
} from '@/services/locker.service'
import { formatDate, formatTime } from '@/lib/utils'
import { toast } from 'sonner'

export default function LockerAccessPage() {
  const [page, setPage] = useState(1)
  const [search, setSearch] = useState('')
  const [accessorTypeFilter, setAccessorTypeFilter] = useState<AccessorType | ''>('')
  const [purposeFilter, setPurposeFilter] = useState<AccessPurpose | ''>('')
  const [isRequestOpen, setIsRequestOpen] = useState(false)
  const [isVerifyOpen, setIsVerifyOpen] = useState(false)
  const [isCompleteOpen, setIsCompleteOpen] = useState(false)
  const [selectedAccess, setSelectedAccess] = useState<LockerAccessLog | null>(null)
  const [activeTab, setActiveTab] = useState('all')

  const queryClient = useQueryClient()

  // Queries
  const { data: accessLogs, isLoading } = useQuery({
    queryKey: ['access-logs', page, search, accessorTypeFilter, purposeFilter, activeTab],
    queryFn: () => {
      const params: any = {
        skip: (page - 1) * 20,
        limit: 20,
      }
      if (accessorTypeFilter) params.accessor_type = accessorTypeFilter
      if (purposeFilter) params.purpose = purposeFilter
      if (activeTab === 'emergency') params.emergency_only = true
      return accessService.listAccessLogs(params)
    },
  })

  const { data: activeSessions } = useQuery({
    queryKey: ['active-sessions'],
    queryFn: () => accessService.getActiveSessions(),
    refetchInterval: 30000, // Refresh every 30 seconds
  })

  const { data: statistics } = useQuery({
    queryKey: ['access-statistics'],
    queryFn: () => accessService.getAccessStatistics(),
  })

  // Mutations
  const requestAccessMutation = useMutation({
    mutationFn: (data: any) => accessService.requestAccess(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['access-logs'] })
      queryClient.invalidateQueries({ queryKey: ['active-sessions'] })
      setIsRequestOpen(false)
      toast.success('Access request created successfully')
    },
    onError: () => {
      toast.error('Failed to create access request')
    },
  })

  const completeAccessMutation = useMutation({
    mutationFn: ({ id, exitTime, remarks }: { id: string; exitTime: string; remarks?: string }) =>
      accessService.completeAccess(id, exitTime, remarks),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['access-logs'] })
      queryClient.invalidateQueries({ queryKey: ['active-sessions'] })
      setIsCompleteOpen(false)
      toast.success('Access completed successfully')
    },
    onError: () => {
      toast.error('Failed to complete access')
    },
  })

  const verifyBiometricMutation = useMutation({
    mutationFn: ({ id, data, verified }: { id: string; data: string; verified: boolean }) =>
      accessService.verifyBiometric(id, data, verified),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['access-logs'] })
      setIsVerifyOpen(false)
      toast.success('Biometric verification recorded')
    },
    onError: () => {
      toast.error('Failed to verify biometric')
    },
  })

  // Helper functions
  const getAccessorTypeColor = (type: AccessorType) => {
    const colors = {
      customer: 'bg-blue-100 text-blue-800',
      joint_holder: 'bg-purple-100 text-purple-800',
      nominee: 'bg-green-100 text-green-800',
      authorized_person: 'bg-yellow-100 text-yellow-800',
      bank_staff: 'bg-gray-100 text-gray-800',
      legal_heir: 'bg-orange-100 text-orange-800',
      court_appointed: 'bg-red-100 text-red-800',
    }
    return colors[type] || 'bg-gray-100 text-gray-800'
  }

  const getPurposeColor = (purpose: AccessPurpose) => {
    const colors = {
      deposit_items: 'bg-green-100 text-green-800',
      retrieve_items: 'bg-blue-100 text-blue-800',
      inspection: 'bg-yellow-100 text-yellow-800',
      inventory_check: 'bg-purple-100 text-purple-800',
      emergency_access: 'bg-red-100 text-red-800',
      maintenance: 'bg-gray-100 text-gray-800',
      legal_requirement: 'bg-orange-100 text-orange-800',
      other: 'bg-gray-100 text-gray-800',
    }
    return colors[purpose] || 'bg-gray-100 text-gray-800'
  }

  const handleCompleteAccess = (access: LockerAccessLog) => {
    setSelectedAccess(access)
    setIsCompleteOpen(true)
  }

  const handleVerifyBiometric = (access: LockerAccessLog) => {
    setSelectedAccess(access)
    setIsVerifyOpen(true)
  }

  return (
    <DashboardLayout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Locker Access Management</h1>
            <p className="text-gray-600 mt-1">Track and manage locker access requests and verifications</p>
          </div>
          <Button onClick={() => setIsRequestOpen(true)}>
            <Plus className="h-4 w-4 mr-2" />
            Request Access
          </Button>
        </div>

        {/* Statistics Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Total Accesses</CardTitle>
              <User className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                {statistics?.data?.total_accesses || 0}
              </div>
              <p className="text-xs text-muted-foreground">All time</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Active Sessions</CardTitle>
              <Clock className="h-4 w-4 text-green-600" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-green-600">
                {activeSessions?.data?.active_sessions?.length || 0}
              </div>
              <p className="text-xs text-muted-foreground">Currently in progress</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Biometric Verified</CardTitle>
              <Fingerprint className="h-4 w-4 text-blue-600" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-blue-600">
                {statistics?.data?.biometric_verification_rate?.toFixed(1) || 0}%
              </div>
              <p className="text-xs text-muted-foreground">Verification rate</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Avg Duration</CardTitle>
              <Clock className="h-4 w-4 text-purple-600" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-purple-600">
                {statistics?.data?.average_duration_minutes?.toFixed(0) || 0}m
              </div>
              <p className="text-xs text-muted-foreground">Average access time</p>
            </CardContent>
          </Card>
        </div>

        {/* Active Sessions Alert */}
        {activeSessions?.data?.active_sessions && activeSessions.data.active_sessions.length > 0 && (
          <Card className="border-l-4 border-l-green-500 bg-green-50">
            <CardHeader>
              <CardTitle className="text-sm font-medium flex items-center gap-2">
                <Clock className="h-4 w-4" />
                Active Access Sessions
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                {activeSessions.data.active_sessions.map((session: LockerAccessLog) => (
                  <div key={session.id} className="flex items-center justify-between p-3 bg-white rounded-lg">
                    <div className="flex items-center gap-3">
                      <Clock className="h-5 w-5 text-green-600" />
                      <div>
                        <p className="font-medium">{session.accessor_name}</p>
                        <p className="text-sm text-gray-600">
                          Locker: {session.locker_id} • Started: {formatTime(session.entry_time)}
                        </p>
                      </div>
                    </div>
                    <Button size="sm" onClick={() => handleCompleteAccess(session)}>
                      <LogOut className="h-4 w-4 mr-2" />
                      Complete
                    </Button>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        )}

        {/* Filters */}
        <Card>
          <CardContent className="pt-6">
            <div className="flex flex-col md:flex-row gap-4">
              <div className="flex-1">
                <Input
                  placeholder="Search by accessor name, locker number..."
                  value={search}
                  onChange={(e) => setSearch(e.target.value)}
                  className="w-full"
                />
              </div>
              <Select value={accessorTypeFilter} onValueChange={(value) => setAccessorTypeFilter(value as AccessorType | '')}>
                <SelectTrigger className="w-full md:w-[200px]">
                  <SelectValue placeholder="Accessor Type" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="">All Types</SelectItem>
                  <SelectItem value={AccessorType.CUSTOMER}>Customer</SelectItem>
                  <SelectItem value={AccessorType.JOINT_HOLDER}>Joint Holder</SelectItem>
                  <SelectItem value={AccessorType.NOMINEE}>Nominee</SelectItem>
                  <SelectItem value={AccessorType.AUTHORIZED_PERSON}>Authorized Person</SelectItem>
                  <SelectItem value={AccessorType.BANK_STAFF}>Bank Staff</SelectItem>
                </SelectContent>
              </Select>
              <Select value={purposeFilter} onValueChange={(value) => setPurposeFilter(value as AccessPurpose | '')}>
                <SelectTrigger className="w-full md:w-[200px]">
                  <SelectValue placeholder="Purpose" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="">All Purposes</SelectItem>
                  <SelectItem value={AccessPurpose.DEPOSIT_ITEMS}>Deposit Items</SelectItem>
                  <SelectItem value={AccessPurpose.RETRIEVE_ITEMS}>Retrieve Items</SelectItem>
                  <SelectItem value={AccessPurpose.INSPECTION}>Inspection</SelectItem>
                  <SelectItem value={AccessPurpose.EMERGENCY_ACCESS}>Emergency</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </CardContent>
        </Card>

        {/* Tabs */}
        <Tabs value={activeTab} onValueChange={setActiveTab}>
          <TabsList>
            <TabsTrigger value="all">All Access</TabsTrigger>
            <TabsTrigger value="today">Today</TabsTrigger>
            <TabsTrigger value="emergency">Emergency</TabsTrigger>
            <TabsTrigger value="register">Access Register</TabsTrigger>
          </TabsList>

          <TabsContent value="all" className="mt-6">
            {isLoading ? (
              <div className="space-y-4">
                {[...Array(5)].map((_, i) => (
                  <Card key={i}>
                    <CardContent className="p-6">
                      <Skeleton className="h-20 w-full" />
                    </CardContent>
                  </Card>
                ))}
              </div>
            ) : (
              <div className="space-y-4">
                {accessLogs?.data?.access_logs?.map((log: LockerAccessLog) => (
                  <Card key={log.id} className="hover:shadow-md transition-shadow">
                    <CardContent className="p-6">
                      <div className="flex items-start justify-between">
                        <div className="flex-1 space-y-3">
                          <div className="flex items-center gap-4">
                            <div className="flex-1">
                              <div className="flex items-center gap-2">
                                <h3 className="font-semibold text-lg">{log.accessor_name}</h3>
                                <Badge className={getAccessorTypeColor(log.accessor_type)}>
                                  {log.accessor_type.replace('_', ' ')}
                                </Badge>
                                <Badge className={getPurposeColor(log.purpose)}>
                                  {log.purpose.replace('_', ' ')}
                                </Badge>
                                {log.emergency_access && (
                                  <Badge className="bg-red-100 text-red-800">
                                    <AlertTriangle className="h-3 w-3 mr-1" />
                                    Emergency
                                  </Badge>
                                )}
                              </div>
                              <p className="text-sm text-gray-600 mt-1">
                                Access Log: {log.access_log_number}
                              </p>
                            </div>
                          </div>

                          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-3">
                            <div>
                              <p className="text-xs text-gray-500">Locker</p>
                              <p className="font-medium">{log.locker_id}</p>
                            </div>
                            <div>
                              <p className="text-xs text-gray-500">Date & Time</p>
                              <p className="font-medium">
                                {formatDate(log.access_date)} {formatTime(log.entry_time)}
                              </p>
                            </div>
                            <div>
                              <p className="text-xs text-gray-500">Duration</p>
                              <p className="font-medium">
                                {log.duration_minutes ? `${log.duration_minutes} min` : 'In progress'}
                              </p>
                            </div>
                            <div>
                              <p className="text-xs text-gray-500">Bank Official</p>
                              <p className="font-medium">{log.bank_official_name}</p>
                            </div>
                          </div>

                          <div className="flex items-center gap-4 mt-3">
                            {log.biometric_verified && (
                              <div className="flex items-center gap-1 text-green-600">
                                <Fingerprint className="h-4 w-4" />
                                <span className="text-sm">Biometric</span>
                              </div>
                            )}
                            {log.photo_captured && (
                              <div className="flex items-center gap-1 text-blue-600">
                                <Camera className="h-4 w-4" />
                                <span className="text-sm">Photo</span>
                              </div>
                            )}
                            {log.signature_captured && (
                              <div className="flex items-center gap-1 text-purple-600">
                                <PenTool className="h-4 w-4" />
                                <span className="text-sm">Signature</span>
                              </div>
                            )}
                            {log.dual_key_used && (
                              <div className="flex items-center gap-1 text-gray-600">
                                <Shield className="h-4 w-4" />
                                <span className="text-sm">Dual Key</span>
                              </div>
                            )}
                          </div>
                        </div>

                        <div className="flex flex-col gap-2">
                          {!log.access_completed && (
                            <Button size="sm" onClick={() => handleCompleteAccess(log)}>
                              <LogOut className="h-4 w-4 mr-2" />
                              Complete
                            </Button>
                          )}
                          {!log.biometric_verified && (
                            <Button size="sm" variant="outline" onClick={() => handleVerifyBiometric(log)}>
                              <Fingerprint className="h-4 w-4 mr-2" />
                              Verify
                            </Button>
                          )}
                          <Button size="sm" variant="ghost">
                            <Eye className="h-4 w-4 mr-2" />
                            Details
                          </Button>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>
            )}
          </TabsContent>

          <TabsContent value="today" className="mt-6">
            <Card>
              <CardContent className="p-6">
                <p className="text-center text-gray-500">Today's access logs will appear here</p>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="emergency" className="mt-6">
            <Card>
              <CardContent className="p-6">
                <p className="text-center text-gray-500">Emergency access logs will appear here</p>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="register" className="mt-6">
            <Card>
              <CardHeader>
                <div className="flex items-center justify-between">
                  <CardTitle>Access Register</CardTitle>
                  <Button variant="outline">
                    <Download className="h-4 w-4 mr-2" />
                    Export Report
                  </Button>
                </div>
              </CardHeader>
              <CardContent>
                <p className="text-center text-gray-500">Select date range to generate access register report</p>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>

        {/* Request Access Dialog */}
        <Dialog open={isRequestOpen} onOpenChange={setIsRequestOpen}>
          <DialogContent className="max-w-2xl">
            <DialogHeader>
              <DialogTitle>Request Locker Access</DialogTitle>
              <DialogDescription>
                Create a new locker access request with dual authentication
              </DialogDescription>
            </DialogHeader>
            <form onSubmit={(e) => {
              e.preventDefault()
              const formData = new FormData(e.currentTarget)
              requestAccessMutation.mutate({
                locker_id: formData.get('locker_id'),
                allocation_id: formData.get('allocation_id'),
                customer_id: formData.get('customer_id'),
                access_date: formData.get('access_date'),
                access_time: formData.get('access_time'),
                accessor_type: formData.get('accessor_type'),
                accessor_name: formData.get('accessor_name'),
                accessor_id: formData.get('accessor_id'),
                purpose: formData.get('purpose'),
                purpose_details: formData.get('purpose_details'),
                bank_official_name: formData.get('bank_official_name'),
                bank_official_employee_id: formData.get('bank_official_employee_id'),
              })
            }}>
              <div className="grid gap-4 py-4">
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <Label htmlFor="locker_id">Locker ID</Label>
                    <Input id="locker_id" name="locker_id" required />
                  </div>
                  <div>
                    <Label htmlFor="allocation_id">Allocation ID</Label>
                    <Input id="allocation_id" name="allocation_id" required />
                  </div>
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
                  <Label htmlFor="accessor_type">Accessor Type</Label>
                  <Select name="accessor_type" required>
                    <SelectTrigger>
                      <SelectValue placeholder="Select accessor type" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value={AccessorType.CUSTOMER}>Customer</SelectItem>
                      <SelectItem value={AccessorType.JOINT_HOLDER}>Joint Holder</SelectItem>
                      <SelectItem value={AccessorType.NOMINEE}>Nominee</SelectItem>
                      <SelectItem value={AccessorType.AUTHORIZED_PERSON}>Authorized Person</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <Label htmlFor="accessor_name">Accessor Name</Label>
                    <Input id="accessor_name" name="accessor_name" required />
                  </div>
                  <div>
                    <Label htmlFor="accessor_id">Accessor ID</Label>
                    <Input id="accessor_id" name="accessor_id" required />
                  </div>
                </div>

                <div>
                  <Label htmlFor="purpose">Purpose</Label>
                  <Select name="purpose" required>
                    <SelectTrigger>
                      <SelectValue placeholder="Select purpose" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value={AccessPurpose.DEPOSIT_ITEMS}>Deposit Items</SelectItem>
                      <SelectItem value={AccessPurpose.RETRIEVE_ITEMS}>Retrieve Items</SelectItem>
                      <SelectItem value={AccessPurpose.INSPECTION}>Inspection</SelectItem>
                      <SelectItem value={AccessPurpose.EMERGENCY_ACCESS}>Emergency Access</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                <div>
                  <Label htmlFor="purpose_details">Purpose Details</Label>
                  <Textarea id="purpose_details" name="purpose_details" rows={3} />
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <Label htmlFor="bank_official_name">Bank Official Name</Label>
                    <Input id="bank_official_name" name="bank_official_name" required />
                  </div>
                  <div>
                    <Label htmlFor="bank_official_employee_id">Employee ID</Label>
                    <Input id="bank_official_employee_id" name="bank_official_employee_id" required />
                  </div>
                </div>
              </div>
              <DialogFooter>
                <Button type="button" variant="outline" onClick={() => setIsRequestOpen(false)}>
                  Cancel
                </Button>
                <Button type="submit" disabled={requestAccessMutation.isPending}>
                  {requestAccessMutation.isPending ? 'Creating...' : 'Create Request'}
                </Button>
              </DialogFooter>
            </form>
          </DialogContent>
        </Dialog>

        {/* Complete Access Dialog */}
        <Dialog open={isCompleteOpen} onOpenChange={setIsCompleteOpen}>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>Complete Access</DialogTitle>
              <DialogDescription>
                Record exit time and complete the access session
              </DialogDescription>
            </DialogHeader>
            <form onSubmit={(e) => {
              e.preventDefault()
              if (!selectedAccess) return
              const formData = new FormData(e.currentTarget)
              completeAccessMutation.mutate({
                id: selectedAccess.id,
                exitTime: formData.get('exit_time') as string,
                remarks: formData.get('remarks') as string,
              })
            }}>
              <div className="grid gap-4 py-4">
                <div>
                  <Label htmlFor="exit_time">Exit Time</Label>
                  <Input 
                    id="exit_time" 
                    name="exit_time" 
                    type="time" 
                    required 
                    defaultValue={new Date().toTimeString().slice(0, 5)}
                  />
                </div>
                <div>
                  <Label htmlFor="remarks">Remarks (Optional)</Label>
                  <Textarea id="remarks" name="remarks" rows={3} />
                </div>
              </div>
              <DialogFooter>
                <Button type="button" variant="outline" onClick={() => setIsCompleteOpen(false)}>
                  Cancel
                </Button>
                <Button type="submit" disabled={completeAccessMutation.isPending}>
                  {completeAccessMutation.isPending ? 'Completing...' : 'Complete Access'}
                </Button>
              </DialogFooter>
            </form>
          </DialogContent>
        </Dialog>

        {/* Verify Biometric Dialog */}
        <Dialog open={isVerifyOpen} onOpenChange={setIsVerifyOpen}>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>Verify Biometric</DialogTitle>
              <DialogDescription>
                Record biometric verification for this access
              </DialogDescription>
            </DialogHeader>
            <form onSubmit={(e) => {
              e.preventDefault()
              if (!selectedAccess) return
              const formData = new FormData(e.currentTarget)
              verifyBiometricMutation.mutate({
                id: selectedAccess.id,
                data: formData.get('biometric_data') as string,
                verified: formData.get('verified') === 'true',
              })
            }}>
              <div className="grid gap-4 py-4">
                <div>
                  <Label htmlFor="biometric_data">Biometric Reference</Label>
                  <Input id="biometric_data" name="biometric_data" required />
                </div>
                <div>
                  <Label htmlFor="verified">Verification Status</Label>
                  <Select name="verified" required>
                    <SelectTrigger>
                      <SelectValue placeholder="Select status" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="true">Verified</SelectItem>
                      <SelectItem value="false">Failed</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>
              <DialogFooter>
                <Button type="button" variant="outline" onClick={() => setIsVerifyOpen(false)}>
                  Cancel
                </Button>
                <Button type="submit" disabled={verifyBiometricMutation.isPending}>
                  {verifyBiometricMutation.isPending ? 'Recording...' : 'Record Verification'}
                </Button>
              </DialogFooter>
            </form>
          </DialogContent>
        </Dialog>
      </div>
    </DashboardLayout>
  )
}
