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
  CreditCard, 
  Plus, 
  Edit, 
  Trash2, 
  CheckCircle2, 
  Star,
  Building2,
  Loader2
} from 'lucide-react'
import { useToast } from '@/components/ui/use-toast'
import { customerService } from '@/services/customer.service'
import type { CustomerBankAccount, AccountType } from '@/types/customer.types'
import { formatDate } from '@/lib/utils'

interface BankAccountsProps {
  customerId: string
}

export function BankAccounts({ customerId }: BankAccountsProps) {
  const { toast } = useToast()
  const queryClient = useQueryClient()
  const [dialogOpen, setDialogOpen] = useState(false)
  const [editingAccount, setEditingAccount] = useState<CustomerBankAccount | null>(null)
  const [verifyDialogOpen, setVerifyDialogOpen] = useState(false)
  const [accountToVerify, setAccountToVerify] = useState<CustomerBankAccount | null>(null)

  // Fetch bank accounts
  const { data: accounts, isLoading } = useQuery({
    queryKey: ['bank-accounts', customerId],
    queryFn: () => customerService.getBankAccounts(customerId),
  })

  // Delete mutation
  const deleteMutation = useMutation({
    mutationFn: (accountId: number) => customerService.deleteBankAccount(customerId, accountId),
    onSuccess: () => {
      toast({
        title: 'Account Deleted',
        description: 'Bank account removed successfully',
      })
      queryClient.invalidateQueries({ queryKey: ['bank-accounts', customerId] })
    },
    onError: (error: any) => {
      toast({
        title: 'Delete Failed',
        description: error.response?.data?.detail || 'An error occurred',
        variant: 'destructive',
      })
    },
  })

  // Set primary mutation
  const setPrimaryMutation = useMutation({
    mutationFn: (accountId: number) => customerService.setPrimaryAccount(customerId, accountId),
    onSuccess: () => {
      toast({
        title: 'Primary Account Updated',
        description: 'Primary account set successfully',
      })
      queryClient.invalidateQueries({ queryKey: ['bank-accounts', customerId] })
    },
    onError: (error: any) => {
      toast({
        title: 'Update Failed',
        description: error.response?.data?.detail || 'An error occurred',
        variant: 'destructive',
      })
    },
  })

  const accountList = accounts?.data || []

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
                <CreditCard className="h-5 w-5" />
                Bank Accounts
              </CardTitle>
              <CardDescription>
                Manage customer bank accounts for disbursement and collection
              </CardDescription>
            </div>
            <Button
              onClick={() => {
                setEditingAccount(null)
                setDialogOpen(true)
              }}
            >
              <Plus className="h-4 w-4 mr-2" />
              Add Account
            </Button>
          </div>
        </CardHeader>
      </Card>

      {/* Bank Accounts List */}
      {accountList.length === 0 ? (
        <Card>
          <CardContent className="py-12">
            <div className="text-center">
              <CreditCard className="h-12 w-12 mx-auto text-gray-400 mb-4" />
              <p className="text-gray-600 mb-4">No bank accounts added yet</p>
              <Button onClick={() => setDialogOpen(true)}>
                <Plus className="h-4 w-4 mr-2" />
                Add First Account
              </Button>
            </div>
          </CardContent>
        </Card>
      ) : (
        <div className="grid grid-cols-1 gap-4">
          {accountList.map((account) => (
            <Card key={account.id}>
              <CardContent className="pt-6">
                <div className="flex items-start justify-between">
                  <div className="flex items-start gap-4 flex-1">
                    <div className="h-12 w-12 bg-primary/10 rounded-lg flex items-center justify-center flex-shrink-0">
                      <Building2 className="h-6 w-6 text-primary" />
                    </div>

                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2 mb-1">
                        <h4 className="font-semibold text-gray-900">
                          {account.bank_name || 'Bank'}
                        </h4>
                        {account.is_primary && (
                          <Badge className="gap-1">
                            <Star className="h-3 w-3" />
                            Primary
                          </Badge>
                        )}
                        {account.is_verified ? (
                          <Badge variant="secondary" className="gap-1 bg-green-100 text-green-800">
                            <CheckCircle2 className="h-3 w-3" />
                            Verified
                          </Badge>
                        ) : (
                          <Badge variant="outline">Not Verified</Badge>
                        )}
                        {!account.is_active && (
                          <Badge variant="secondary">Inactive</Badge>
                        )}
                      </div>

                      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-3">
                        <InfoItem label="Account Number" value={`****${account.account_number.slice(-4)}`} />
                        <InfoItem label="Account Holder" value={account.account_holder_name} />
                        <InfoItem label="Account Type" value={account.account_type} />
                        <InfoItem label="IFSC Code" value={account.ifsc_code} />
                        {account.branch_name && (
                          <InfoItem label="Branch" value={account.branch_name} />
                        )}
                        {account.verified_date && (
                          <InfoItem label="Verified On" value={formatDate(account.verified_date)} />
                        )}
                      </div>

                      <div className="flex items-center gap-4 mt-3 text-sm text-gray-600">
                        {account.use_for_disbursement && (
                          <span className="flex items-center gap-1">
                            <CheckCircle2 className="h-4 w-4 text-green-600" />
                            Disbursement
                          </span>
                        )}
                        {account.use_for_collection && (
                          <span className="flex items-center gap-1">
                            <CheckCircle2 className="h-4 w-4 text-green-600" />
                            Collection
                          </span>
                        )}
                      </div>
                    </div>
                  </div>

                  <div className="flex items-center gap-2 ml-4">
                    {!account.is_primary && (
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => setPrimaryMutation.mutate(account.id)}
                        disabled={setPrimaryMutation.isPending}
                      >
                        Set Primary
                      </Button>
                    )}
                    {!account.is_verified && (
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => {
                          setAccountToVerify(account)
                          setVerifyDialogOpen(true)
                        }}
                      >
                        Verify
                      </Button>
                    )}
                    <Button
                      variant="ghost"
                      size="icon"
                      onClick={() => {
                        setEditingAccount(account)
                        setDialogOpen(true)
                      }}
                    >
                      <Edit className="h-4 w-4" />
                    </Button>
                    <Button
                      variant="ghost"
                      size="icon"
                      onClick={() => {
                        if (confirm('Are you sure you want to remove this account?')) {
                          deleteMutation.mutate(account.id)
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

      {/* Add/Edit Dialog */}
      <BankAccountDialog
        open={dialogOpen}
        onOpenChange={setDialogOpen}
        customerId={customerId}
        editingAccount={editingAccount}
      />

      {/* Verify Dialog */}
      <VerifyAccountDialog
        open={verifyDialogOpen}
        onOpenChange={setVerifyDialogOpen}
        customerId={customerId}
        account={accountToVerify}
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

function BankAccountDialog({
  open,
  onOpenChange,
  customerId,
  editingAccount,
}: {
  open: boolean
  onOpenChange: (open: boolean) => void
  customerId: string
  editingAccount: CustomerBankAccount | null
}) {
  const { toast } = useToast()
  const queryClient = useQueryClient()
  const [formData, setFormData] = useState<Partial<CustomerBankAccount>>(
    editingAccount || {
      bank_id: 0,
      account_number: '',
      account_holder_name: '',
      account_type: 'savings' as AccountType,
      ifsc_code: '',
      is_primary: false,
      use_for_disbursement: true,
      use_for_collection: true,
    }
  )

  const saveMutation = useMutation({
    mutationFn: () => {
      if (editingAccount) {
        return customerService.updateBankAccount(customerId, editingAccount.id, formData)
      }
      return customerService.addBankAccount(customerId, formData)
    },
    onSuccess: () => {
      toast({
        title: editingAccount ? 'Account Updated' : 'Account Added',
        description: 'Bank account saved successfully',
      })
      queryClient.invalidateQueries({ queryKey: ['bank-accounts', customerId] })
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
      <DialogContent className="max-w-2xl">
        <DialogHeader>
          <DialogTitle>{editingAccount ? 'Edit' : 'Add'} Bank Account</DialogTitle>
          <DialogDescription>
            {editingAccount ? 'Update' : 'Add new'} bank account details
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div className="col-span-2 space-y-2">
              <Label htmlFor="bank">Bank Name *</Label>
              <Select
                value={formData.bank_id?.toString()}
                onValueChange={(value) => setFormData({ ...formData, bank_id: parseInt(value) })}
              >
                <SelectTrigger>
                  <SelectValue placeholder="Select bank" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="1">State Bank of India</SelectItem>
                  <SelectItem value="2">HDFC Bank</SelectItem>
                  <SelectItem value="3">ICICI Bank</SelectItem>
                  <SelectItem value="4">Axis Bank</SelectItem>
                  <SelectItem value="5">Punjab National Bank</SelectItem>
                  <SelectItem value="6">Bank of Baroda</SelectItem>
                  <SelectItem value="7">Canara Bank</SelectItem>
                  <SelectItem value="8">Union Bank of India</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-2">
              <Label htmlFor="account-number">Account Number *</Label>
              <Input
                id="account-number"
                value={formData.account_number}
                onChange={(e) => setFormData({ ...formData, account_number: e.target.value })}
                placeholder="Enter account number"
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="account-holder">Account Holder Name *</Label>
              <Input
                id="account-holder"
                value={formData.account_holder_name}
                onChange={(e) => setFormData({ ...formData, account_holder_name: e.target.value })}
                placeholder="As per bank records"
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="account-type">Account Type *</Label>
              <Select
                value={formData.account_type}
                onValueChange={(value) => setFormData({ ...formData, account_type: value as AccountType })}
              >
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="savings">Savings</SelectItem>
                  <SelectItem value="current">Current</SelectItem>
                  <SelectItem value="overdraft">Overdraft</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-2">
              <Label htmlFor="ifsc">IFSC Code *</Label>
              <Input
                id="ifsc"
                value={formData.ifsc_code}
                onChange={(e) => setFormData({ ...formData, ifsc_code: e.target.value.toUpperCase() })}
                placeholder="e.g., SBIN0001234"
                maxLength={11}
              />
            </div>
          </div>

          {/* Checkboxes */}
          <div className="space-y-3 border-t pt-4">
            <div className="flex items-center space-x-2">
              <Checkbox
                id="primary"
                checked={formData.is_primary}
                onCheckedChange={(checked) => setFormData({ ...formData, is_primary: !!checked })}
              />
              <Label htmlFor="primary" className="font-normal cursor-pointer">
                Set as primary account
              </Label>
            </div>

            <div className="flex items-center space-x-2">
              <Checkbox
                id="disbursement"
                checked={formData.use_for_disbursement}
                onCheckedChange={(checked) => setFormData({ ...formData, use_for_disbursement: !!checked })}
              />
              <Label htmlFor="disbursement" className="font-normal cursor-pointer">
                Use for loan disbursement
              </Label>
            </div>

            <div className="flex items-center space-x-2">
              <Checkbox
                id="collection"
                checked={formData.use_for_collection}
                onCheckedChange={(checked) => setFormData({ ...formData, use_for_collection: !!checked })}
              />
              <Label htmlFor="collection" className="font-normal cursor-pointer">
                Use for EMI collection
              </Label>
            </div>
          </div>
        </div>

        <DialogFooter>
          <Button variant="outline" onClick={() => onOpenChange(false)}>
            Cancel
          </Button>
          <Button
            onClick={() => saveMutation.mutate()}
            disabled={
              !formData.bank_id ||
              !formData.account_number ||
              !formData.account_holder_name ||
              !formData.ifsc_code ||
              saveMutation.isPending
            }
          >
            {saveMutation.isPending && (
              <Loader2 className="h-4 w-4 mr-2 animate-spin" />
            )}
            {editingAccount ? 'Update' : 'Add'} Account
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}

function VerifyAccountDialog({
  open,
  onOpenChange,
  customerId,
  account,
}: {
  open: boolean
  onOpenChange: (open: boolean) => void
  customerId: string
  account: CustomerBankAccount | null
}) {
  const { toast } = useToast()
  const queryClient = useQueryClient()
  const [method, setMethod] = useState('penny_drop')
  const [remarks, setRemarks] = useState('')

  const verifyMutation = useMutation({
    mutationFn: () => {
      if (!account) throw new Error('No account selected')
      return customerService.verifyAccount(customerId, account.id, method, remarks)
    },
    onSuccess: () => {
      toast({
        title: 'Account Verified',
        description: 'Bank account verified successfully',
      })
      queryClient.invalidateQueries({ queryKey: ['bank-accounts', customerId] })
      onOpenChange(false)
      setRemarks('')
    },
    onError: (error: any) => {
      toast({
        title: 'Verification Failed',
        description: error.response?.data?.detail || 'An error occurred',
        variant: 'destructive',
      })
    },
  })

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Verify Bank Account</DialogTitle>
          <DialogDescription>
            Verify account: {account?.account_number}
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="method">Verification Method</Label>
            <Select value={method} onValueChange={setMethod}>
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="penny_drop">Penny Drop (₹1 transfer)</SelectItem>
                <SelectItem value="statement">Bank Statement</SelectItem>
                <SelectItem value="passbook">Physical Passbook</SelectItem>
              </SelectContent>
            </Select>
          </div>

          <div className="space-y-2">
            <Label htmlFor="remarks">Remarks (Optional)</Label>
            <Input
              id="remarks"
              value={remarks}
              onChange={(e) => setRemarks(e.target.value)}
              placeholder="Add verification notes"
            />
          </div>

          {method === 'penny_drop' && (
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
              <p className="text-sm text-blue-900">
                A small amount (₹1) will be deposited to verify the account. 
                The amount will be credited within 24 hours.
              </p>
            </div>
          )}
        </div>

        <DialogFooter>
          <Button variant="outline" onClick={() => onOpenChange(false)}>
            Cancel
          </Button>
          <Button onClick={() => verifyMutation.mutate()} disabled={verifyMutation.isPending}>
            {verifyMutation.isPending && (
              <Loader2 className="h-4 w-4 mr-2 animate-spin" />
            )}
            Verify Account
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}
