'use client'

import { useEffect, useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useParams, useRouter } from 'next/navigation'
import { useForm } from 'react-hook-form'
import { ArrowLeft, Save, Loader2 } from 'lucide-react'
import Link from 'next/link'
import { DashboardLayout } from '@/components/layout/dashboard-layout'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
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
import { toast } from 'sonner'
import { contractService, type ContractType, type ContractStatus } from '@/services/contract.service'

interface ContractFormData {
  title: string
  description: string
  status: ContractStatus
  effective_date: string
  expiry_date: string
  execution_date: string
  contract_value: string
  currency: string
  is_renewable: boolean
  auto_renewal: boolean
  renewal_notice_days: string
  alert_before_expiry_days: string
  document_url: string
  notes: string
}

export default function EditContractPage() {
  const params = useParams()
  const router = useRouter()
  const queryClient = useQueryClient()
  const contractId = params.id as string
  const [isSubmitting, setIsSubmitting] = useState(false)

  const { data: contractData, isLoading } = useQuery({
    queryKey: ['contract', contractId],
    queryFn: () => contractService.getContract(contractId),
    enabled: !!contractId,
  })

  const contract = contractData?.data?.data

  const { register, handleSubmit, formState: { errors }, setValue, watch, reset } = useForm<ContractFormData>()

  useEffect(() => {
    if (contract) {
      reset({
        title: contract.title,
        description: contract.description || '',
        status: contract.status,
        effective_date: contract.effective_date,
        expiry_date: contract.expiry_date || '',
        execution_date: contract.execution_date || '',
        contract_value: contract.contract_value?.toString() || '',
        currency: contract.currency,
        is_renewable: contract.is_renewable,
        auto_renewal: contract.auto_renewal,
        renewal_notice_days: contract.renewal_notice_days.toString(),
        alert_before_expiry_days: contract.alert_before_expiry_days.toString(),
        document_url: contract.document_url || '',
        notes: contract.notes || '',
      })
    }
  }, [contract, reset])

  const updateMutation = useMutation({
    mutationFn: (data: any) => contractService.updateContract(contractId, data),
    onSuccess: () => {
      toast.success('Contract updated successfully')
      queryClient.invalidateQueries({ queryKey: ['contract', contractId] })
      queryClient.invalidateQueries({ queryKey: ['contracts'] })
      router.push(`/legal/contracts/${contractId}`)
    },
    onError: (error: any) => {
      toast.error(error?.response?.data?.error?.message || 'Failed to update contract')
      setIsSubmitting(false)
    },
  })

  const onSubmit = (data: ContractFormData) => {
    setIsSubmitting(true)
    
    const payload = {
      title: data.title,
      description: data.description || undefined,
      status: data.status,
      effective_date: data.effective_date,
      expiry_date: data.expiry_date || undefined,
      execution_date: data.execution_date || undefined,
      contract_value: data.contract_value ? parseFloat(data.contract_value) : undefined,
      currency: data.currency,
      is_renewable: data.is_renewable,
      auto_renewal: data.auto_renewal,
      renewal_notice_days: parseInt(data.renewal_notice_days),
      alert_before_expiry_days: parseInt(data.alert_before_expiry_days),
      document_url: data.document_url || undefined,
      notes: data.notes || undefined,
    }

    updateMutation.mutate(payload)
  }

  const isRenewable = watch('is_renewable')

  if (isLoading) {
    return (
      <DashboardLayout>
        <div className="flex items-center justify-center h-96">
          <Loader2 className="h-8 w-8 animate-spin text-gray-400" />
        </div>
      </DashboardLayout>
    )
  }

  if (!contract) {
    return (
      <DashboardLayout>
        <div className="text-center py-12">
          <p className="text-gray-600">Contract not found</p>
          <Link href="/legal/contracts">
            <Button className="mt-4">Back to Contracts</Button>
          </Link>
        </div>
      </DashboardLayout>
    )
  }

  return (
    <DashboardLayout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center gap-4">
          <Link href={`/legal/contracts/${contractId}`}>
            <Button variant="outline" size="sm">
              <ArrowLeft className="h-4 w-4 mr-2" />
              Back
            </Button>
          </Link>
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Edit Contract</h1>
            <p className="text-gray-600 mt-1">{contract.contract_number}</p>
          </div>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit(onSubmit)}>
          <div className="space-y-6">
            {/* Basic Information */}
            <Card>
              <CardHeader>
                <CardTitle>Basic Information</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {/* Title */}
                  <div className="md:col-span-2">
                    <Label htmlFor="title">Contract Title *</Label>
                    <Input
                      id="title"
                      {...register('title', { required: 'Title is required' })}
                      placeholder="Enter contract title"
                    />
                    {errors.title && (
                      <p className="text-sm text-red-600 mt-1">{errors.title.message}</p>
                    )}
                  </div>

                  {/* Status */}
                  <div>
                    <Label htmlFor="status">Status *</Label>
                    <Select
                      defaultValue={contract.status}
                      onValueChange={(value) => setValue('status', value as ContractStatus)}
                    >
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="draft">Draft</SelectItem>
                        <SelectItem value="under_review">Under Review</SelectItem>
                        <SelectItem value="pending_approval">Pending Approval</SelectItem>
                        <SelectItem value="approved">Approved</SelectItem>
                        <SelectItem value="active">Active</SelectItem>
                        <SelectItem value="expired">Expired</SelectItem>
                        <SelectItem value="terminated">Terminated</SelectItem>
                        <SelectItem value="renewed">Renewed</SelectItem>
                        <SelectItem value="cancelled">Cancelled</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>

                  {/* Contract Value */}
                  <div>
                    <Label htmlFor="contract_value">Contract Value</Label>
                    <Input
                      id="contract_value"
                      type="number"
                      step="0.01"
                      {...register('contract_value')}
                      placeholder="0.00"
                    />
                  </div>

                  {/* Currency */}
                  <div>
                    <Label htmlFor="currency">Currency</Label>
                    <Select
                      defaultValue={contract.currency}
                      onValueChange={(value) => setValue('currency', value)}
                    >
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="INR">INR</SelectItem>
                        <SelectItem value="USD">USD</SelectItem>
                        <SelectItem value="EUR">EUR</SelectItem>
                        <SelectItem value="GBP">GBP</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>

                  {/* Description */}
                  <div className="md:col-span-2">
                    <Label htmlFor="description">Description</Label>
                    <Textarea
                      id="description"
                      {...register('description')}
                      placeholder="Enter contract description"
                      rows={3}
                    />
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Dates */}
            <Card>
              <CardHeader>
                <CardTitle>Contract Dates</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  {/* Effective Date */}
                  <div>
                    <Label htmlFor="effective_date">Effective Date *</Label>
                    <Input
                      id="effective_date"
                      type="date"
                      {...register('effective_date', { required: 'Effective date is required' })}
                    />
                    {errors.effective_date && (
                      <p className="text-sm text-red-600 mt-1">{errors.effective_date.message}</p>
                    )}
                  </div>

                  {/* Expiry Date */}
                  <div>
                    <Label htmlFor="expiry_date">Expiry Date</Label>
                    <Input
                      id="expiry_date"
                      type="date"
                      {...register('expiry_date')}
                    />
                  </div>

                  {/* Execution Date */}
                  <div>
                    <Label htmlFor="execution_date">Execution Date</Label>
                    <Input
                      id="execution_date"
                      type="date"
                      {...register('execution_date')}
                    />
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Renewal Settings */}
            <Card>
              <CardHeader>
                <CardTitle>Renewal Settings</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {/* Is Renewable */}
                  <div className="flex items-center space-x-2">
                    <input
                      type="checkbox"
                      id="is_renewable"
                      {...register('is_renewable')}
                      className="h-4 w-4 rounded border-gray-300"
                    />
                    <Label htmlFor="is_renewable" className="font-normal cursor-pointer">
                      Contract is renewable
                    </Label>
                  </div>

                  {/* Auto Renewal */}
                  {isRenewable && (
                    <div className="flex items-center space-x-2">
                      <input
                        type="checkbox"
                        id="auto_renewal"
                        {...register('auto_renewal')}
                        className="h-4 w-4 rounded border-gray-300"
                      />
                      <Label htmlFor="auto_renewal" className="font-normal cursor-pointer">
                        Enable auto-renewal
                      </Label>
                    </div>
                  )}

                  {/* Renewal Notice Days */}
                  {isRenewable && (
                    <div>
                      <Label htmlFor="renewal_notice_days">Renewal Notice (Days)</Label>
                      <Input
                        id="renewal_notice_days"
                        type="number"
                        {...register('renewal_notice_days')}
                        placeholder="90"
                      />
                    </div>
                  )}

                  {/* Alert Before Expiry */}
                  <div>
                    <Label htmlFor="alert_before_expiry_days">Alert Before Expiry (Days)</Label>
                    <Input
                      id="alert_before_expiry_days"
                      type="number"
                      {...register('alert_before_expiry_days')}
                      placeholder="30"
                    />
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Additional Information */}
            <Card>
              <CardHeader>
                <CardTitle>Additional Information</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="space-y-4">
                  {/* Document URL */}
                  <div>
                    <Label htmlFor="document_url">Document URL</Label>
                    <Input
                      id="document_url"
                      {...register('document_url')}
                      placeholder="https://example.com/contract.pdf"
                    />
                  </div>

                  {/* Notes */}
                  <div>
                    <Label htmlFor="notes">Notes</Label>
                    <Textarea
                      id="notes"
                      {...register('notes')}
                      placeholder="Add any additional notes"
                      rows={4}
                    />
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Form Actions */}
            <div className="flex justify-end gap-4">
              <Link href={`/legal/contracts/${contractId}`}>
                <Button type="button" variant="outline">
                  Cancel
                </Button>
              </Link>
              <Button type="submit" disabled={isSubmitting}>
                <Save className="h-4 w-4 mr-2" />
                {isSubmitting ? 'Saving...' : 'Save Changes'}
              </Button>
            </div>
          </div>
        </form>
      </div>
    </DashboardLayout>
  )
}
