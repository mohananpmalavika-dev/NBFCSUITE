'use client'

import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Plus, Search, Filter, Edit, Trash2, MapPin, Archive, Box } from 'lucide-react'
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
import { lockerService, LockerSize, LockerStatus, type LockerMaster } from '@/services/locker.service'
import { formatCurrency } from '@/lib/utils'
import { toast } from 'sonner'

export default function LockerMasterPage() {
  const [page, setPage] = useState(1)
  const [search, setSearch] = useState('')
  const [sizeFilter, setSizeFilter] = useState<LockerSize | ''>('')
  const [statusFilter, setStatusFilter] = useState<LockerStatus | ''>('')
  const [isCreateOpen, setIsCreateOpen] = useState(false)
  const [isEditOpen, setIsEditOpen] = useState(false)
  const [selectedLocker, setSelectedLocker] = useState<LockerMaster | null>(null)

  const queryClient = useQueryClient()

  const { data, isLoading } = useQuery({
    queryKey: ['lockers', page, search, sizeFilter, statusFilter],
    queryFn: () => lockerService.getLockers({
      skip: (page - 1) * 12,
      limit: 12,
      locker_size: sizeFilter || undefined,
      status: statusFilter || undefined,
    }),
  })

  const { data: statsData } = useQuery({
    queryKey: ['locker-occupancy-stats'],
    queryFn: () => lockerService.getOccupancyStats(),
  })

  const createMutation = useMutation({
    mutationFn: (data: Partial<LockerMaster>) => lockerService.createLocker(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['lockers'] })
      queryClient.invalidateQueries({ queryKey: ['locker-occupancy-stats'] })
      setIsCreateOpen(false)
      toast.success('Locker created successfully')
    },
    onError: () => {
      toast.error('Failed to create locker')
    },
  })

  const updateMutation = useMutation({
    mutationFn: ({ id, data }: { id: string; data: Partial<LockerMaster> }) =>
      lockerService.updateLocker(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['lockers'] })
      setIsEditOpen(false)
      toast.success('Locker updated successfully')
    },
    onError: () => {
      toast.error('Failed to update locker')
    },
  })

  const deleteMutation = useMutation({
    mutationFn: (id: string) => lockerService.deleteLocker(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['lockers'] })
      queryClient.invalidateQueries({ queryKey: ['locker-occupancy-stats'] })
      toast.success('Locker deleted successfully')
    },
    onError: () => {
      toast.error('Failed to delete locker')
    },
  })

  const getStatusColor = (status: LockerStatus) => {
    const colors = {
      available: 'bg-green-100 text-green-800',
      allocated: 'bg-blue-100 text-blue-800',
      under_maintenance: 'bg-yellow-100 text-yellow-800',
      blocked: 'bg-red-100 text-red-800',
      damaged: 'bg-orange-100 text-orange-800',
      retired: 'bg-gray-100 text-gray-800',
    }
    return colors[status] || 'bg-gray-100 text-gray-800'
  }

  const getSizeLabel = (size: LockerSize) => {
    const labels = {
      small: 'Small (5"×5"×20")',
      medium: 'Medium (5"×10"×20")',
      large: 'Large (10"×10"×20")',
      extra_large: 'Extra Large (10"×20"×20")',
    }
    return labels[size] || size
  }

  const handleEdit = (locker: LockerMaster) => {
    setSelectedLocker(locker)
    setIsEditOpen(true)
  }

  const handleDelete = (id: string) => {
    if (confirm('Are you sure you want to delete this locker?')) {
      deleteMutation.mutate(id)
    }
  }

  return (
    <DashboardLayout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Locker Master</h1>
            <p className="text-gray-600 mt-1">Manage locker inventory and availability</p>
          </div>
          <Button onClick={() => setIsCreateOpen(true)}>
            <Plus className="h-4 w-4 mr-2" />
            Add Locker
          </Button>
        </div>

        {/* Stats Cards */}
        {statsData?.data && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Total Lockers</CardTitle>
                <Box className="h-4 w-4 text-gray-600" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{statsData.data.total_lockers}</div>
              </CardContent>
            </Card>
            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Available</CardTitle>
                <Archive className="h-4 w-4 text-green-600" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-green-600">
                  {statsData.data.available_lockers}
                </div>
              </CardContent>
            </Card>
            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Allocated</CardTitle>
                <MapPin className="h-4 w-4 text-blue-600" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-blue-600">
                  {statsData.data.allocated_lockers}
                </div>
              </CardContent>
            </Card>
            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Occupancy Rate</CardTitle>
                <Box className="h-4 w-4 text-purple-600" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-purple-600">
                  {statsData.data.occupancy_rate}%
                </div>
              </CardContent>
            </Card>
          </div>
        )}

        {/* Filters */}
        <div className="flex items-center gap-4">
          <div className="flex-1 relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
            <Input
              type="search"
              placeholder="Search by locker number, location..."
              className="pl-10"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
            />
          </div>
          <Select value={sizeFilter} onValueChange={(value) => setSizeFilter(value as LockerSize | '')}>
            <SelectTrigger className="w-[180px]">
              <SelectValue placeholder="All Sizes" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="">All Sizes</SelectItem>
              <SelectItem value={LockerSize.SMALL}>Small</SelectItem>
              <SelectItem value={LockerSize.MEDIUM}>Medium</SelectItem>
              <SelectItem value={LockerSize.LARGE}>Large</SelectItem>
              <SelectItem value={LockerSize.EXTRA_LARGE}>Extra Large</SelectItem>
            </SelectContent>
          </Select>
          <Select value={statusFilter} onValueChange={(value) => setStatusFilter(value as LockerStatus | '')}>
            <SelectTrigger className="w-[180px]">
              <SelectValue placeholder="All Status" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="">All Status</SelectItem>
              <SelectItem value={LockerStatus.AVAILABLE}>Available</SelectItem>
              <SelectItem value={LockerStatus.ALLOCATED}>Allocated</SelectItem>
              <SelectItem value={LockerStatus.UNDER_MAINTENANCE}>Under Maintenance</SelectItem>
              <SelectItem value={LockerStatus.BLOCKED}>Blocked</SelectItem>
            </SelectContent>
          </Select>
          <Button variant="outline">
            <Filter className="h-4 w-4 mr-2" />
            More Filters
          </Button>
        </div>

        {/* Lockers Table */}
        <Card>
          <CardContent className="p-0">
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="bg-gray-50 border-b">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Locker Details
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Location
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Size
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Annual Rent
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Status
                    </th>
                    <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Actions
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {isLoading ? (
                    [...Array(5)].map((_, i) => (
                      <tr key={i}>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <Skeleton className="h-4 w-32" />
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <Skeleton className="h-4 w-40" />
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <Skeleton className="h-4 w-24" />
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <Skeleton className="h-4 w-20" />
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <Skeleton className="h-6 w-20" />
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-right">
                          <Skeleton className="h-8 w-20 ml-auto" />
                        </td>
                      </tr>
                    ))
                  ) : data?.data?.lockers && data.data.lockers.length > 0 ? (
                    data.data.lockers.map((locker: LockerMaster) => (
                      <tr key={locker.id} className="hover:bg-gray-50">
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div className="text-sm font-medium text-gray-900">
                            {locker.locker_number}
                          </div>
                          <div className="text-sm text-gray-500">{locker.locker_id}</div>
                        </td>
                        <td className="px-6 py-4">
                          <div className="text-sm text-gray-900">{locker.vault_room}</div>
                          <div className="text-sm text-gray-500">
                            {locker.floor && `Floor: ${locker.floor}`}
                            {locker.rack_number && ` | Rack: ${locker.rack_number}`}
                          </div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div className="text-sm text-gray-900">
                            {getSizeLabel(locker.locker_size)}
                          </div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div className="text-sm font-medium text-gray-900">
                            {formatCurrency(locker.annual_rent)}
                          </div>
                          <div className="text-xs text-gray-500">
                            Deposit: {formatCurrency(locker.security_deposit)}
                          </div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <Badge className={getStatusColor(locker.status)}>
                            {locker.status.replace('_', ' ').toUpperCase()}
                          </Badge>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                          <div className="flex items-center justify-end gap-2">
                            <Button
                              variant="ghost"
                              size="sm"
                              onClick={() => handleEdit(locker)}
                            >
                              <Edit className="h-4 w-4" />
                            </Button>
                            <Button
                              variant="ghost"
                              size="sm"
                              onClick={() => handleDelete(locker.id)}
                              disabled={locker.status === LockerStatus.ALLOCATED}
                            >
                              <Trash2 className="h-4 w-4" />
                            </Button>
                          </div>
                        </td>
                      </tr>
                    ))
                  ) : (
                    <tr>
                      <td colSpan={6} className="px-6 py-12 text-center text-gray-500">
                        No lockers found
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
          </CardContent>
        </Card>

        {/* Create/Edit Dialogs will be added here */}
        <LockerFormDialog
          open={isCreateOpen}
          onOpenChange={setIsCreateOpen}
          onSubmit={(data) => createMutation.mutate(data)}
          isLoading={createMutation.isPending}
        />
        
        {selectedLocker && (
          <LockerFormDialog
            open={isEditOpen}
            onOpenChange={setIsEditOpen}
            locker={selectedLocker}
            onSubmit={(data) => updateMutation.mutate({ id: selectedLocker.id, data })}
            isLoading={updateMutation.isPending}
          />
        )}
      </div>
    </DashboardLayout>
  )
}

// Locker Form Dialog Component
function LockerFormDialog({
  open,
  onOpenChange,
  locker,
  onSubmit,
  isLoading,
}: {
  open: boolean
  onOpenChange: (open: boolean) => void
  locker?: LockerMaster
  onSubmit: (data: Partial<LockerMaster>) => void
  isLoading: boolean
}) {
  const [formData, setFormData] = useState<Partial<LockerMaster>>(
    locker || {
      locker_number: '',
      locker_id: '',
      locker_size: LockerSize.MEDIUM,
      vault_room: '',
      floor: '',
      rack_number: '',
      position: '',
      locker_type: 'dual_key',
      lock_type: 'mechanical',
      annual_rent: 0,
      security_deposit: 0,
      status: LockerStatus.AVAILABLE,
      is_available: true,
    }
  )

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    onSubmit(formData)
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>{locker ? 'Edit Locker' : 'Create New Locker'}</DialogTitle>
          <DialogDescription>
            {locker ? 'Update locker details' : 'Add a new locker to the inventory'}
          </DialogDescription>
        </DialogHeader>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="locker_number">Locker Number *</Label>
              <Input
                id="locker_number"
                value={formData.locker_number}
                onChange={(e) => setFormData({ ...formData, locker_number: e.target.value })}
                required
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="locker_id">Locker ID *</Label>
              <Input
                id="locker_id"
                value={formData.locker_id}
                onChange={(e) => setFormData({ ...formData, locker_id: e.target.value })}
                required
              />
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="locker_size">Size *</Label>
              <Select
                value={formData.locker_size}
                onValueChange={(value) => setFormData({ ...formData, locker_size: value as LockerSize })}
              >
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value={LockerSize.SMALL}>Small (5"×5"×20")</SelectItem>
                  <SelectItem value={LockerSize.MEDIUM}>Medium (5"×10"×20")</SelectItem>
                  <SelectItem value={LockerSize.LARGE}>Large (10"×10"×20")</SelectItem>
                  <SelectItem value={LockerSize.EXTRA_LARGE}>Extra Large (10"×20"×20")</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div className="space-y-2">
              <Label htmlFor="vault_room">Vault Room *</Label>
              <Input
                id="vault_room"
                value={formData.vault_room}
                onChange={(e) => setFormData({ ...formData, vault_room: e.target.value })}
                required
              />
            </div>
          </div>

          <div className="grid grid-cols-3 gap-4">
            <div className="space-y-2">
              <Label htmlFor="floor">Floor</Label>
              <Input
                id="floor"
                value={formData.floor || ''}
                onChange={(e) => setFormData({ ...formData, floor: e.target.value })}
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="rack_number">Rack Number</Label>
              <Input
                id="rack_number"
                value={formData.rack_number || ''}
                onChange={(e) => setFormData({ ...formData, rack_number: e.target.value })}
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="position">Position</Label>
              <Input
                id="position"
                value={formData.position || ''}
                onChange={(e) => setFormData({ ...formData, position: e.target.value })}
              />
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="annual_rent">Annual Rent (₹) *</Label>
              <Input
                id="annual_rent"
                type="number"
                value={formData.annual_rent}
                onChange={(e) => setFormData({ ...formData, annual_rent: parseFloat(e.target.value) })}
                required
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="security_deposit">Security Deposit (₹) *</Label>
              <Input
                id="security_deposit"
                type="number"
                value={formData.security_deposit}
                onChange={(e) => setFormData({ ...formData, security_deposit: parseFloat(e.target.value) })}
                required
              />
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="locker_type">Locker Type</Label>
              <Select
                value={formData.locker_type}
                onValueChange={(value) => setFormData({ ...formData, locker_type: value })}
              >
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="single_key">Single Key</SelectItem>
                  <SelectItem value="dual_key">Dual Key</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div className="space-y-2">
              <Label htmlFor="lock_type">Lock Type</Label>
              <Select
                value={formData.lock_type}
                onValueChange={(value) => setFormData({ ...formData, lock_type: value })}
              >
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="mechanical">Mechanical</SelectItem>
                  <SelectItem value="electronic">Electronic</SelectItem>
                  <SelectItem value="biometric">Biometric</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>

          <DialogFooter>
            <Button type="button" variant="outline" onClick={() => onOpenChange(false)}>
              Cancel
            </Button>
            <Button type="submit" disabled={isLoading}>
              {isLoading ? 'Saving...' : locker ? 'Update' : 'Create'}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  )
}
