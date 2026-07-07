'use client'

import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useParams, useRouter } from 'next/navigation'
import { 
  Plus, 
  Edit,
  Trash2,
  ArrowLeft,
  RefreshCw,
  ArrowRightLeft,
  TrendingUp,
  TrendingDown,
  Calendar,
  CheckCircle,
  XCircle,
  AlertCircle
} from 'lucide-react'
import { DashboardLayout } from '@/components/layout/dashboard-layout'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { Badge } from '@/components/ui/badge'
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog'
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table'
import { depositService } from '@/services/deposit.service'
import { formatCurrency, formatDate } from '@/lib/utils'
import { useToast } from '@/hooks/use-toast'
import { Alert, AlertDescription } from '@/components/ui/alert'

export default function StandingInstructionsPage() {
  const params = useParams()
  const router = useRouter()
  const { toast } = useToast()
  const queryClient = useQueryClient()
  const accountId = parseInt(params.accountId as string)

  const [isCreateDialogOpen, setIsCreateDialogOpen] = useState(false)
  const [instructionType, setInstructionType] = useState('auto_debit')
  const [amount, setAmount] = useState('')
  const [frequency, setFrequency] = useState('monthly')
  const [sourceAccount, setSourceAccount] = useState('')
  const [targetAccount, setTargetAccount] = useState('')
  const [startDate, setStartDate] = useState('')
  const [endDate, setEndDate] = useState('')
  const [minBalanceThreshold, setMinBalanceThreshold] = useState('')
  const [maxBalanceThreshold, setMaxBalanceThreshold] = useState('')

  // Fetch standing instructions
  const { data: instructionsData, isLoading } = useQuery({
    queryKey: ['standing-instructions', accountId],
    queryFn: () => depositService.getStandingInstructions(accountId),
  })

  // Fetch account details
  const { data: accountData } = useQuery({
    queryKey: ['deposit-account', accountId],
    queryFn: () => depositService.getAccount(accountId.toString()),
  })

  // Create instruction mutation
  const createMutation = useMutation({
    mutationFn: (data: any) => depositService.createStandingInstruction(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['standing-instructions', accountId] })
      setIsCreateDialogOpen(false)
      resetForm()
      toast({
        title: 'Success',
        description: 'Standing instruction created successfully',
      })
    },
    onError: () => {
      toast({
        title: 'Error',
        description: 'Failed to create standing instruction',
        variant: 'destructive',
      })
    },
  })

  // Cancel instruction mutation
  const cancelMutation = useMutation({
    mutationFn: (instructionId: number) =>
      depositService.cancelStandingInstruction(instructionId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['standing-instructions', accountId] })
      toast({
        title: 'Success',
        description: 'Standing instruction cancelled',
      })
    },
    onError: () => {
      toast({
        title: 'Error',
        description: 'Failed to cancel instruction',
        variant: 'destructive',
      })
    },
  })

  const handleCreate = () => {
    if (!startDate) {
      toast({
        title: 'Validation Error',
        description: 'Please select start date',
        variant: 'destructive',
      })
      return
    }

    const data: any = {
      account_id: accountId,
      instruction_type: instructionType,
      frequency: frequency,
      start_date: startDate,
      end_date: endDate || undefined,
    }

    if (instructionType === 'auto_debit' || instructionType === 'recurring_transfer') {
      if (!amount) {
        toast({
          title: 'Validation Error',
          description: 'Please enter amount',
          variant: 'destructive',
        })
        return
      }
      data.amount = parseFloat(amount)
    }

    if (instructionType === 'sweep_in' || instructionType === 'sweep_out') {
      if (!minBalanceThreshold && !maxBalanceThreshold) {
        toast({
          title: 'Validation Error',
          description: 'Please enter balance thresholds',
          variant: 'destructive',
        })
        return
      }
      if (minBalanceThreshold) data.min_balance_threshold = parseFloat(minBalanceThreshold)
      if (maxBalanceThreshold) data.max_balance_threshold = parseFloat(maxBalanceThreshold)
    }

    if (sourceAccount) data.source_account = sourceAccount
    if (targetAccount) data.target_account = targetAccount

    createMutation.mutate(data)
  }

  const handleCancel = (instructionId: number) => {
    if (confirm('Are you sure you want to cancel this standing instruction?')) {
      cancelMutation.mutate(instructionId)
    }
  }

  const resetForm = () => {
    setInstructionType('auto_debit')
    setAmount('')
    setFrequency('monthly')
    setSourceAccount('')
    setTargetAccount('')
    setStartDate('')
    setEndDate('')
    setMinBalanceThreshold('')
    setMaxBalanceThreshold('')
  }

  const getInstructionIcon = (type: string) => {
    switch (type) {
      case 'auto_debit':
        return <ArrowRightLeft className="h-4 w-4" />
      case 'sweep_in':
        return <TrendingUp className="h-4 w-4" />
      case 'sweep_out':
        return <TrendingDown className="h-4 w-4" />
      case 'recurring_transfer':
        return <RefreshCw className="h-4 w-4" />
      default:
        return <Calendar className="h-4 w-4" />
    }
  }

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'active':
        return <Badge className="bg-green-100 text-green-800">Active</Badge>
      case 'suspended':
        return <Badge className="bg-yellow-100 text-yellow-800">Suspended</Badge>
      case 'cancelled':
        return <Badge className="bg-gray-100 text-gray-800">Cancelled</Badge>
      case 'completed':
        return <Badge className="bg-blue-100 text-blue-800">Completed</Badge>
      default:
        return <Badge variant="outline">{status}</Badge>
    }
  }

  return (
    <DashboardLayout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <Button variant="ghost" onClick={() => router.back()}>
              <ArrowLeft className="h-4 w-4 mr-2" />
              Back
            </Button>
            <div>
              <h1 className="text-3xl font-bold text-gray-900">Standing Instructions</h1>
              {accountData && (
                <p className="text-gray-600 mt-1">
                  Account: {accountData.data?.account_number} - {accountData.data?.customer_name}
                </p>
              )}
            </div>
          </div>
          <Dialog open={isCreateDialogOpen} onOpenChange={setIsCreateDialogOpen}>
            <DialogTrigger asChild>
              <Button>
                <Plus className="h-4 w-4 mr-2" />
                Create Instruction
              </Button>
            </DialogTrigger>
            <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
              <DialogHeader>
                <DialogTitle>Create Standing Instruction</DialogTitle>
              </DialogHeader>
              <div className="space-y-4">
                <div className="space-y-2">
                  <Label htmlFor="instructionType">Instruction Type</Label>
                  <Select value={instructionType} onValueChange={setInstructionType}>
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="auto_debit">Auto Debit</SelectItem>
                      <SelectItem value="sweep_in">Sweep In</SelectItem>
                      <SelectItem value="sweep_out">Sweep Out</SelectItem>
                      <SelectItem value="recurring_transfer">Recurring Transfer</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                {(instructionType === 'auto_debit' || instructionType === 'recurring_transfer') && (
                  <div className="space-y-2">
                    <Label htmlFor="amount">Amount</Label>
                    <Input
                      id="amount"
                      type="number"
                      placeholder="Enter amount"
                      value={amount}
                      onChange={(e) => setAmount(e.target.value)}
                    />
                  </div>
                )}

                {(instructionType === 'sweep_in' || instructionType === 'sweep_out') && (
                  <div className="grid grid-cols-2 gap-4">
                    <div className="space-y-2">
                      <Label htmlFor="minBalance">Min Balance Threshold</Label>
                      <Input
                        id="minBalance"
                        type="number"
                        placeholder="Minimum balance"
                        value={minBalanceThreshold}
                        onChange={(e) => setMinBalanceThreshold(e.target.value)}
                      />
                    </div>
                    <div className="space-y-2">
                      <Label htmlFor="maxBalance">Max Balance Threshold</Label>
                      <Input
                        id="maxBalance"
                        type="number"
                        placeholder="Maximum balance"
                        value={maxBalanceThreshold}
                        onChange={(e) => setMaxBalanceThreshold(e.target.value)}
                      />
                    </div>
                  </div>
                )}

                <div className="space-y-2">
                  <Label htmlFor="frequency">Frequency</Label>
                  <Select value={frequency} onValueChange={setFrequency}>
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="daily">Daily</SelectItem>
                      <SelectItem value="weekly">Weekly</SelectItem>
                      <SelectItem value="monthly">Monthly</SelectItem>
                      <SelectItem value="on_threshold">On Threshold</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="sourceAccount">Source Account (Optional)</Label>
                    <Input
                      id="sourceAccount"
                      placeholder="Source account"
                      value={sourceAccount}
                      onChange={(e) => setSourceAccount(e.target.value)}
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="targetAccount">Target Account (Optional)</Label>
                    <Input
                      id="targetAccount"
                      placeholder="Target account"
                      value={targetAccount}
                      onChange={(e) => setTargetAccount(e.target.value)}
                    />
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="startDate">Start Date</Label>
                    <Input
                      id="startDate"
                      type="date"
                      value={startDate}
                      onChange={(e) => setStartDate(e.target.value)}
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="endDate">End Date (Optional)</Label>
                    <Input
                      id="endDate"
                      type="date"
                      value={endDate}
                      onChange={(e) => setEndDate(e.target.value)}
                      min={startDate}
                    />
                  </div>
                </div>

                <Button
                  onClick={handleCreate}
                  disabled={createMutation.isPending}
                  className="w-full"
                >
                  {createMutation.isPending ? 'Creating...' : 'Create Instruction'}
                </Button>
              </div>
            </DialogContent>
          </Dialog>
        </div>

        {/* Instructions List */}
        <Card>
          <CardHeader>
            <CardTitle>Active Standing Instructions</CardTitle>
          </CardHeader>
          <CardContent>
            {isLoading ? (
              <div className="space-y-2">
                {[1, 2, 3].map((i) => (
                  <div key={i} className="h-16 bg-gray-100 rounded animate-pulse" />
                ))}
              </div>
            ) : (
              <div className="overflow-x-auto">
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Type</TableHead>
                      <TableHead>Amount / Threshold</TableHead>
                      <TableHead>Frequency</TableHead>
                      <TableHead>Start Date</TableHead>
                      <TableHead>Next Execution</TableHead>
                      <TableHead>Executed</TableHead>
                      <TableHead>Status</TableHead>
                      <TableHead>Actions</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {instructionsData?.data?.instructions?.map((instruction: any) => (
                      <TableRow key={instruction.id}>
                        <TableCell>
                          <div className="flex items-center gap-2">
                            {getInstructionIcon(instruction.instruction_type)}
                            <span className="font-medium capitalize">
                              {instruction.instruction_type.replace('_', ' ')}
                            </span>
                          </div>
                        </TableCell>
                        <TableCell>
                          {instruction.amount ? (
                            formatCurrency(instruction.amount)
                          ) : (
                            <span className="text-sm text-gray-600">
                              {instruction.min_balance_threshold &&
                                `Min: ${formatCurrency(instruction.min_balance_threshold)}`}
                              {instruction.max_balance_threshold &&
                                ` Max: ${formatCurrency(instruction.max_balance_threshold)}`}
                            </span>
                          )}
                        </TableCell>
                        <TableCell className="capitalize">{instruction.frequency}</TableCell>
                        <TableCell>{formatDate(instruction.start_date)}</TableCell>
                        <TableCell>
                          {instruction.next_execution_date
                            ? formatDate(instruction.next_execution_date)
                            : '-'}
                        </TableCell>
                        <TableCell>
                          <Badge variant="outline">{instruction.execution_count || 0} times</Badge>
                        </TableCell>
                        <TableCell>{getStatusBadge(instruction.status)}</TableCell>
                        <TableCell>
                          <div className="flex gap-2">
                            <Button
                              variant="ghost"
                              size="sm"
                              onClick={() => handleCancel(instruction.id)}
                              disabled={
                                instruction.status === 'cancelled' ||
                                instruction.status === 'completed' ||
                                cancelMutation.isPending
                              }
                            >
                              <Trash2 className="h-4 w-4" />
                            </Button>
                          </div>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
                {(!instructionsData?.data?.instructions ||
                  instructionsData.data.instructions.length === 0) && (
                  <div className="text-center py-12 text-gray-500">
                    <Calendar className="h-16 w-16 mx-auto mb-4 opacity-50" />
                    <p className="text-lg font-medium">No standing instructions found</p>
                    <p className="text-sm mt-1">Create your first standing instruction</p>
                  </div>
                )}
              </div>
            )}
          </CardContent>
        </Card>

        {/* Info Card */}
        <Alert>
          <AlertCircle className="h-4 w-4" />
          <AlertDescription>
            <strong>Standing Instructions:</strong> Automate recurring transactions like EMI payments,
            sweep operations, and scheduled transfers. Instructions are executed automatically based on
            the configured frequency and rules.
          </AlertDescription>
        </Alert>

        {/* Instruction Types Info */}
        <Card className="bg-gray-50 border-gray-200">
          <CardContent className="pt-6">
            <h3 className="font-semibold mb-3">Instruction Types</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
              <div>
                <div className="flex items-center gap-2 font-medium mb-1">
                  <ArrowRightLeft className="h-4 w-4 text-blue-600" />
                  Auto Debit
                </div>
                <p className="text-gray-600">
                  Automatically debit a fixed amount at regular intervals (e.g., for loan EMI, RD
                  installments)
                </p>
              </div>
              <div>
                <div className="flex items-center gap-2 font-medium mb-1">
                  <TrendingUp className="h-4 w-4 text-green-600" />
                  Sweep In
                </div>
                <p className="text-gray-600">
                  Transfer funds into this account when balance falls below threshold
                </p>
              </div>
              <div>
                <div className="flex items-center gap-2 font-medium mb-1">
                  <TrendingDown className="h-4 w-4 text-orange-600" />
                  Sweep Out
                </div>
                <p className="text-gray-600">
                  Transfer excess funds when balance exceeds threshold
                </p>
              </div>
              <div>
                <div className="flex items-center gap-2 font-medium mb-1">
                  <RefreshCw className="h-4 w-4 text-purple-600" />
                  Recurring Transfer
                </div>
                <p className="text-gray-600">
                  Schedule recurring transfers to another account at fixed intervals
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </DashboardLayout>
  )
}
