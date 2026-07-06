'use client'

import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Checkbox } from '@/components/ui/checkbox'
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
import { 
  Users, 
  Plus, 
  Edit, 
  Trash2, 
  Heart, 
  Phone, 
  AlertCircle,
  Loader2
} from 'lucide-react'
import { useToast } from '@/components/ui/use-toast'
import { customerService } from '@/services/customer.service'
import type { CustomerFamily, Gender } from '@/types/customer.types'
import { formatDate } from '@/lib/utils'

interface FamilyTreeProps {
  customerId: string
}

export function FamilyTree({ customerId }: FamilyTreeProps) {
  const { toast } = useToast()
  const queryClient = useQueryClient()
  const [dialogOpen, setDialogOpen] = useState(false)
  const [editingMember, setEditingMember] = useState<CustomerFamily | null>(null)

  // Fetch family members
  const { data: familyMembers, isLoading } = useQuery({
    queryKey: ['family-members', customerId],
    queryFn: () => customerService.getFamilyMembers(customerId),
  })

  // Validate nominees
  const { data: nomineeValidation } = useQuery({
    queryKey: ['nominee-validation', customerId],
    queryFn: () => customerService.validateNominees(customerId),
    enabled: !!familyMembers?.data,
  })

  // Delete mutation
  const deleteMutation = useMutation({
    mutationFn: (memberId: number) => customerService.deleteFamilyMember(customerId, memberId),
    onSuccess: () => {
      toast({
        title: 'Member Deleted',
        description: 'Family member removed successfully',
      })
      queryClient.invalidateQueries({ queryKey: ['family-members', customerId] })
      queryClient.invalidateQueries({ queryKey: ['nominee-validation', customerId] })
    },
    onError: (error: any) => {
      toast({
        title: 'Delete Failed',
        description: error.response?.data?.detail || 'An error occurred',
        variant: 'destructive',
      })
    },
  })

  const members = familyMembers?.data || []
  const nominees = members.filter((m) => m.is_nominee)
  const emergencyContacts = members.filter((m) => m.is_emergency_contact)

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-12">
        <Loader2 className="h-8 w-8 animate-spin text-gray-400" />
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header Card */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle className="flex items-center gap-2">
                <Users className="h-5 w-5" />
                Family Members
              </CardTitle>
              <CardDescription>
                Manage family members, nominees, and emergency contacts
              </CardDescription>
            </div>
            <Button
              onClick={() => {
                setEditingMember(null)
                setDialogOpen(true)
              }}
            >
              <Plus className="h-4 w-4 mr-2" />
              Add Member
            </Button>
          </div>
        </CardHeader>
      </Card>

      {/* Nominee Validation Alert */}
      {nominees.length > 0 && nomineeValidation?.data && !nomineeValidation.data.valid && (
        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4 flex items-start gap-3">
          <AlertCircle className="h-5 w-5 text-yellow-600 flex-shrink-0 mt-0.5" />
          <div>
            <p className="font-medium text-yellow-900">Nominee Percentage Invalid</p>
            <p className="text-sm text-yellow-800 mt-1">
              Total nominee percentage: {nomineeValidation.data.total_percentage}%. 
              Must equal 100% for valid nomination.
            </p>
          </div>
        </div>
      )}

      {/* Family Members List */}
      {members.length === 0 ? (
        <Card>
          <CardContent className="py-12">
            <div className="text-center">
              <Users className="h-12 w-12 mx-auto text-gray-400 mb-4" />
              <p className="text-gray-600 mb-4">No family members added yet</p>
              <Button onClick={() => setDialogOpen(true)}>
                <Plus className="h-4 w-4 mr-2" />
                Add First Member
              </Button>
            </div>
          </CardContent>
        </Card>
      ) : (
        <div className="grid grid-cols-1 gap-4">
          {members.map((member) => (
            <Card key={member.id}>
              <CardContent className="pt-6">
                <div className="flex items-start justify-between">
                  <div className="flex items-start gap-4 flex-1">
                    <div className="h-12 w-12 bg-primary/10 rounded-full flex items-center justify-center flex-shrink-0">
                      <Users className="h-6 w-6 text-primary" />
                    </div>

                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2 mb-1">
                        <h4 className="font-semibold text-gray-900">{member.name}</h4>
                        {member.is_nominee && (
                          <Badge variant="secondary" className="gap-1">
                            <Heart className="h-3 w-3" />
                            Nominee {member.nominee_percentage}%
                          </Badge>
                        )}
                        {member.is_emergency_contact && (
                          <Badge variant="outline" className="gap-1">
                            <Phone className="h-3 w-3" />
                            Emergency
                          </Badge>
                        )}
                        {member.is_dependent && (
                          <Badge variant="outline">Dependent</Badge>
                        )}
                      </div>

                      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-3">
                        <InfoItem label="Relationship" value={member.relationship_type_name || '-'} />
                        <InfoItem label="Age" value={member.age ? `${member.age} years` : '-'} />
                        <InfoItem label="Gender" value={member.gender || '-'} />
                        <InfoItem label="Mobile" value={member.mobile || '-'} />
                        {member.occupation && (
                          <InfoItem label="Occupation" value={member.occupation} />
                        )}
                        {member.monthly_income && (
                          <InfoItem 
                            label="Monthly Income" 
                            value={`₹${member.monthly_income.toLocaleString('en-IN')}`} 
                          />
                        )}
                        {member.date_of_birth && (
                          <InfoItem label="Date of Birth" value={formatDate(member.date_of_birth)} />
                        )}
                      </div>
                    </div>
                  </div>

                  <div className="flex items-center gap-2 ml-4">
                    <Button
                      variant="ghost"
                      size="icon"
                      onClick={() => {
                        setEditingMember(member)
                        setDialogOpen(true)
                      }}
                    >
                      <Edit className="h-4 w-4" />
                    </Button>
                    <Button
                      variant="ghost"
                      size="icon"
                      onClick={() => {
                        if (confirm('Are you sure you want to remove this family member?')) {
                          deleteMutation.mutate(member.id)
                        }
                      }}
                      disabled={deleteMutation.isPending}
                    >
                      <Trash2 className="h-4 w-4 text-red-600" />
                    </Button>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      {/* Summary Cards */}
      {members.length > 0 && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <Card>
            <CardContent className="pt-6">
              <div className="text-center">
                <Users className="h-8 w-8 mx-auto text-gray-400 mb-2" />
                <p className="text-2xl font-bold text-gray-900">{members.length}</p>
                <p className="text-sm text-gray-600">Total Members</p>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="pt-6">
              <div className="text-center">
                <Heart className="h-8 w-8 mx-auto text-red-400 mb-2" />
                <p className="text-2xl font-bold text-gray-900">{nominees.length}</p>
                <p className="text-sm text-gray-600">Nominees</p>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="pt-6">
              <div className="text-center">
                <Phone className="h-8 w-8 mx-auto text-blue-400 mb-2" />
                <p className="text-2xl font-bold text-gray-900">{emergencyContacts.length}</p>
                <p className="text-sm text-gray-600">Emergency Contacts</p>
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Add/Edit Dialog */}
      <FamilyMemberDialog
        open={dialogOpen}
        onOpenChange={setDialogOpen}
        customerId={customerId}
        editingMember={editingMember}
      />
    </div>
  )
}

function InfoItem({ label, value }: { label: string; value: string }) {
  return (
    <div>
      <p className="text-xs text-gray-600">{label}</p>
      <p className="text-sm font-medium text-gray-900">{value}</p>
    </div>
  )
}

function FamilyMemberDialog({
  open,
  onOpenChange,
  customerId,
  editingMember,
}: {
  open: boolean
  onOpenChange: (open: boolean) => void
  customerId: string
  editingMember: CustomerFamily | null
}) {
  const { toast } = useToast()
  const queryClient = useQueryClient()
  const [formData, setFormData] = useState<Partial<CustomerFamily>>(
    editingMember || {
      name: '',
      relationship_type_id: 0,
      date_of_birth: '',
      gender: 'male' as Gender,
      mobile: '',
      occupation: '',
      monthly_income: 0,
      is_dependent: true,
      is_emergency_contact: false,
      is_nominee: false,
      nominee_percentage: 0,
    }
  )

  const saveMutation = useMutation({
    mutationFn: () => {
      if (editingMember) {
        return customerService.updateFamilyMember(customerId, editingMember.id, formData)
      }
      return customerService.addFamilyMember(customerId, formData)
    },
    onSuccess: () => {
      toast({
        title: editingMember ? 'Member Updated' : 'Member Added',
        description: 'Family member saved successfully',
      })
      queryClient.invalidateQueries({ queryKey: ['family-members', customerId] })
      queryClient.invalidateQueries({ queryKey: ['nominee-validation', customerId] })
      onOpenChange(false)
    },
    onError: (error: any) => {
      toast({
        title: 'Save Failed',
        description: error.response?.data?.detail || 'An error occurred',
        variant: 'destructive',
      })
    },
  })

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>{editingMember ? 'Edit' : 'Add'} Family Member</DialogTitle>
          <DialogDescription>
            {editingMember ? 'Update' : 'Add new'} family member details
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div className="col-span-2 space-y-2">
              <Label htmlFor="name">Full Name *</Label>
              <Input
                id="name"
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                placeholder="Enter full name"
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="relationship">Relationship *</Label>
              <Select
                value={formData.relationship_type_id?.toString()}
                onValueChange={(value) => setFormData({ ...formData, relationship_type_id: parseInt(value) })}
              >
                <SelectTrigger>
                  <SelectValue placeholder="Select relationship" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="1">Father</SelectItem>
                  <SelectItem value="2">Mother</SelectItem>
                  <SelectItem value="3">Spouse</SelectItem>
                  <SelectItem value="4">Son</SelectItem>
                  <SelectItem value="5">Daughter</SelectItem>
                  <SelectItem value="6">Brother</SelectItem>
                  <SelectItem value="7">Sister</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-2">
              <Label htmlFor="gender">Gender</Label>
              <Select
                value={formData.gender}
                onValueChange={(value) => setFormData({ ...formData, gender: value as Gender })}
              >
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="male">Male</SelectItem>
                  <SelectItem value="female">Female</SelectItem>
                  <SelectItem value="other">Other</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-2">
              <Label htmlFor="dob">Date of Birth</Label>
              <Input
                id="dob"
                type="date"
                value={formData.date_of_birth}
                onChange={(e) => setFormData({ ...formData, date_of_birth: e.target.value })}
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="mobile">Mobile Number</Label>
              <Input
                id="mobile"
                value={formData.mobile}
                onChange={(e) => setFormData({ ...formData, mobile: e.target.value })}
                placeholder="10-digit mobile"
                maxLength={10}
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="occupation">Occupation</Label>
              <Input
                id="occupation"
                value={formData.occupation}
                onChange={(e) => setFormData({ ...formData, occupation: e.target.value })}
                placeholder="Enter occupation"
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="income">Monthly Income</Label>
              <Input
                id="income"
                type="number"
                value={formData.monthly_income}
                onChange={(e) => setFormData({ ...formData, monthly_income: parseFloat(e.target.value) || 0 })}
                placeholder="0"
              />
            </div>
          </div>

          {/* Checkboxes */}
          <div className="space-y-3 border-t pt-4">
            <div className="flex items-center space-x-2">
              <Checkbox
                id="dependent"
                checked={formData.is_dependent}
                onCheckedChange={(checked) => setFormData({ ...formData, is_dependent: !!checked })}
              />
              <Label htmlFor="dependent" className="font-normal cursor-pointer">
                Mark as dependent
              </Label>
            </div>

            <div className="flex items-center space-x-2">
              <Checkbox
                id="emergency"
                checked={formData.is_emergency_contact}
                onCheckedChange={(checked) => setFormData({ ...formData, is_emergency_contact: !!checked })}
              />
              <Label htmlFor="emergency" className="font-normal cursor-pointer">
                Mark as emergency contact
              </Label>
            </div>

            <div className="flex items-center space-x-2">
              <Checkbox
                id="nominee"
                checked={formData.is_nominee}
                onCheckedChange={(checked) => setFormData({ ...formData, is_nominee: !!checked })}
              />
              <Label htmlFor="nominee" className="font-normal cursor-pointer">
                Mark as nominee
              </Label>
            </div>

            {formData.is_nominee && (
              <div className="ml-6 space-y-2">
                <Label htmlFor="percentage">Nominee Percentage (%)</Label>
                <Input
                  id="percentage"
                  type="number"
                  min="0"
                  max="100"
                  value={formData.nominee_percentage}
                  onChange={(e) => setFormData({ ...formData, nominee_percentage: parseFloat(e.target.value) || 0 })}
                  placeholder="0-100"
                />
                <p className="text-xs text-gray-600">
                  Total nominee percentage must equal 100%
                </p>
              </div>
            )}
          </div>
        </div>

        <DialogFooter>
          <Button variant="outline" onClick={() => onOpenChange(false)}>
            Cancel
          </Button>
          <Button
            onClick={() => saveMutation.mutate()}
            disabled={!formData.name || !formData.relationship_type_id || saveMutation.isPending}
          >
            {saveMutation.isPending && (
              <Loader2 className="h-4 w-4 mr-2 animate-spin" />
            )}
            {editingMember ? 'Update' : 'Add'} Member
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}
