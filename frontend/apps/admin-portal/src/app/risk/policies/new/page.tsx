'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { useMutation } from '@tanstack/react-query'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import * as z from 'zod'
import { ArrowLeft, Save, Plus, X } from 'lucide-react'
import Link from 'next/link'
import { DashboardLayout } from '@/components/layout/dashboard-layout'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { riskService } from '@/services/risk.service'
import { toast } from 'sonner'

const policySchema = z.object({
  policy_code: z.string().min(3, 'Policy code must be at least 3 characters'),
  policy_name: z.string().min(3, 'Policy name must be at least 3 characters'),
  policy_version: z.string().min(1, 'Version is required'),
  description: z.string().optional(),
  
  // Applicability
  product_types: z.array(z.string()).min(1, 'Select at least one product type'),
  customer_segments: z.array(z.string()).min(1, 'Select at least one customer segment'),
  
  // Credit Criteria
  min_cibil_score: z.number().min(300).max(900),
  max_debt_to_income_ratio: z.number().min(0).max(100),
  min_monthly_income: z.number().min(0),
  
  // Loan Limits
  min_loan_amount: z.number().min(0),
  max_loan_amount: z.number().min(0),
  min_tenure_months: z.number().min(1),
  max_tenure_months: z.number().min(1),
  
  // Age & Employment
  min_age: z.number().min(18).max(100),
  max_age: z.number().min(18).max(100),
  min_years_in_employment: z.number().min(0),
  self_employed_allowed: z.boolean(),
  
  // Other
  allowed_states: z.array(z.string()).optional(),
  negative_geographies: z.array(z.string()).optional(),
  negative_professions: z.array(z.string()).optional(),
  required_documents: z.array(z.string()).optional(),
  
  effective_from: z.string(),
  effective_to: z.string().optional(),
  is_active: z.boolean(),
})

type PolicyFormData = z.infer<typeof policySchema>

const PRODUCT_TYPES = ['personal_loan', 'business_loan', 'home_loan', 'gold_loan', 'vehicle_loan']
const CUSTOMER_SEGMENTS = ['salaried', 'self_employed', 'business', 'professional', 'pensioner']
const PROFESSIONS = ['Real Estate Agent', 'Stock Market Trader', 'Jeweler', 'Politician', 'Lawyer']
const INDIAN_STATES = [
  'Andhra Pradesh', 'Arunachal Pradesh', 'Assam', 'Bihar', 'Chhattisgarh',
  'Goa', 'Gujarat', 'Haryana', 'Himachal Pradesh', 'Jharkhand',
  'Karnataka', 'Kerala', 'Madhya Pradesh', 'Maharashtra', 'Manipur',
  'Meghalaya', 'Mizoram', 'Nagaland', 'Odisha', 'Punjab',
  'Rajasthan', 'Sikkim', 'Tamil Nadu', 'Telangana', 'Tripura',
  'Uttar Pradesh', 'Uttarakhand', 'West Bengal'
]
const DOCUMENTS = ['PAN Card', 'Aadhaar Card', 'Bank Statements (6 months)', 'ITR (2 years)', 'Salary Slips (3 months)', 'Business Proof']

export default function NewCreditPolicyPage() {
  const router = useRouter()
  const [selectedProducts, setSelectedProducts] = useState<string[]>([])
  const [selectedSegments, setSelectedSegments] = useState<string[]>([])
  const [selectedStates, setSelectedStates] = useState<string[]>([])
  const [negativeStates, setNegativeStates] = useState<string[]>([])
  const [negativeProfessions, setNegativeProfessions] = useState<string[]>([])
  const [selectedDocuments, setSelectedDocuments] = useState<string[]>([])

  const {
    register,
    handleSubmit,
    formState: { errors },
    setValue,
    watch,
  } = useForm<PolicyFormData>({
    resolver: zodResolver(policySchema),
    defaultValues: {
      policy_version: '1.0',
      min_cibil_score: 650,
      max_debt_to_income_ratio: 50,
      min_monthly_income: 25000,
      min_age: 21,
      max_age: 65,
      min_years_in_employment: 2,
      self_employed_allowed: true,
      is_active: true,
      effective_from: new Date().toISOString().split('T')[0],
    },
  })

  const createMutation = useMutation({
    mutationFn: (data: PolicyFormData) => riskService.createCreditPolicy(data),
    onSuccess: () => {
      toast.success('Credit policy created successfully')
      router.push('/risk/policies')
    },
    onError: (error: any) => {
      toast.error(error.message || 'Failed to create credit policy')
    },
  })

  const onSubmit = (data: PolicyFormData) => {
    // Set array values from state
    data.product_types = selectedProducts
    data.customer_segments = selectedSegments
    data.allowed_states = selectedStates.length > 0 ? selectedStates : undefined
    data.negative_geographies = negativeStates.length > 0 ? negativeStates : undefined
    data.negative_professions = negativeProfessions.length > 0 ? negativeProfessions : undefined
    data.required_documents = selectedDocuments.length > 0 ? selectedDocuments : undefined

    createMutation.mutate(data)
  }

  const toggleItem = (item: string, list: string[], setList: (list: string[]) => void) => {
    if (list.includes(item)) {
      setList(list.filter(i => i !== item))
    } else {
      setList([...list, item])
    }
  }

  return (
    <DashboardLayout>
      <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <Link href="/risk/policies">
              <Button variant="ghost" size="sm">
                <ArrowLeft className="h-4 w-4 mr-2" />
                Back
              </Button>
            </Link>
            <div>
              <h1 className="text-3xl font-bold text-gray-900">Create Credit Policy</h1>
              <p className="text-gray-600 mt-1">Define a new credit policy with eligibility rules</p>
            </div>
          </div>
          <div className="flex gap-2">
            <Link href="/risk/policies">
              <Button variant="outline" type="button">Cancel</Button>
            </Link>
            <Button type="submit" disabled={createMutation.isPending}>
              <Save className="h-4 w-4 mr-2" />
              {createMutation.isPending ? 'Saving...' : 'Save Policy'}
            </Button>
          </div>
        </div>

        {/* Basic Information */}
        <Card>
          <CardHeader>
            <CardTitle>Basic Information</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div>
                <label className="text-sm font-medium mb-1 block">Policy Code *</label>
                <Input {...register('policy_code')} placeholder="CP-2024-001" />
                {errors.policy_code && (
                  <p className="text-sm text-red-600 mt-1">{errors.policy_code.message}</p>
                )}
              </div>
              <div>
                <label className="text-sm font-medium mb-1 block">Policy Name *</label>
                <Input {...register('policy_name')} placeholder="Salaried Personal Loan Policy" />
                {errors.policy_name && (
                  <p className="text-sm text-red-600 mt-1">{errors.policy_name.message}</p>
                )}
              </div>
              <div>
                <label className="text-sm font-medium mb-1 block">Version *</label>
                <Input {...register('policy_version')} placeholder="1.0" />
                {errors.policy_version && (
                  <p className="text-sm text-red-600 mt-1">{errors.policy_version.message}</p>
                )}
              </div>
            </div>
            <div>
              <label className="text-sm font-medium mb-1 block">Description</label>
              <textarea
                {...register('description')}
                className="flex min-h-[80px] w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
                placeholder="Policy description..."
              />
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="text-sm font-medium mb-1 block">Effective From *</label>
                <Input type="date" {...register('effective_from')} />
              </div>
              <div>
                <label className="text-sm font-medium mb-1 block">Effective To</label>
                <Input type="date" {...register('effective_to')} />
              </div>
            </div>
            <div className="flex items-center gap-2">
              <input
                type="checkbox"
                id="is_active"
                {...register('is_active')}
                className="h-4 w-4 rounded border-gray-300"
              />
              <label htmlFor="is_active" className="text-sm font-medium">Active</label>
            </div>
          </CardContent>
        </Card>

        {/* Applicability */}
        <Card>
          <CardHeader>
            <CardTitle>Applicability</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <label className="text-sm font-medium mb-2 block">Product Types *</label>
              <div className="flex flex-wrap gap-2">
                {PRODUCT_TYPES.map(product => (
                  <Badge
                    key={product}
                    variant={selectedProducts.includes(product) ? 'default' : 'outline'}
                    className="cursor-pointer"
                    onClick={() => toggleItem(product, selectedProducts, setSelectedProducts)}
                  >
                    {product.replace('_', ' ')}
                  </Badge>
                ))}
              </div>
              {errors.product_types && (
                <p className="text-sm text-red-600 mt-1">{errors.product_types.message}</p>
              )}
            </div>
            <div>
              <label className="text-sm font-medium mb-2 block">Customer Segments *</label>
              <div className="flex flex-wrap gap-2">
                {CUSTOMER_SEGMENTS.map(segment => (
                  <Badge
                    key={segment}
                    variant={selectedSegments.includes(segment) ? 'default' : 'outline'}
                    className="cursor-pointer"
                    onClick={() => toggleItem(segment, selectedSegments, setSelectedSegments)}
                  >
                    {segment.replace('_', ' ')}
                  </Badge>
                ))}
              </div>
              {errors.customer_segments && (
                <p className="text-sm text-red-600 mt-1">{errors.customer_segments.message}</p>
              )}
            </div>
          </CardContent>
        </Card>

        {/* Credit Criteria */}
        <Card>
          <CardHeader>
            <CardTitle>Credit Criteria</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div>
                <label className="text-sm font-medium mb-1 block">Min CIBIL Score *</label>
                <Input
                  type="number"
                  {...register('min_cibil_score', { valueAsNumber: true })}
                  placeholder="650"
                />
                {errors.min_cibil_score && (
                  <p className="text-sm text-red-600 mt-1">{errors.min_cibil_score.message}</p>
                )}
              </div>
              <div>
                <label className="text-sm font-medium mb-1 block">Max Debt-to-Income Ratio (%) *</label>
                <Input
                  type="number"
                  {...register('max_debt_to_income_ratio', { valueAsNumber: true })}
                  placeholder="50"
                />
                {errors.max_debt_to_income_ratio && (
                  <p className="text-sm text-red-600 mt-1">{errors.max_debt_to_income_ratio.message}</p>
                )}
              </div>
              <div>
                <label className="text-sm font-medium mb-1 block">Min Monthly Income (₹) *</label>
                <Input
                  type="number"
                  {...register('min_monthly_income', { valueAsNumber: true })}
                  placeholder="25000"
                />
                {errors.min_monthly_income && (
                  <p className="text-sm text-red-600 mt-1">{errors.min_monthly_income.message}</p>
                )}
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Loan Limits */}
        <Card>
          <CardHeader>
            <CardTitle>Loan Parameters</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="text-sm font-medium mb-1 block">Min Loan Amount (₹) *</label>
                <Input
                  type="number"
                  {...register('min_loan_amount', { valueAsNumber: true })}
                  placeholder="50000"
                />
                {errors.min_loan_amount && (
                  <p className="text-sm text-red-600 mt-1">{errors.min_loan_amount.message}</p>
                )}
              </div>
              <div>
                <label className="text-sm font-medium mb-1 block">Max Loan Amount (₹) *</label>
                <Input
                  type="number"
                  {...register('max_loan_amount', { valueAsNumber: true })}
                  placeholder="1000000"
                />
                {errors.max_loan_amount && (
                  <p className="text-sm text-red-600 mt-1">{errors.max_loan_amount.message}</p>
                )}
              </div>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="text-sm font-medium mb-1 block">Min Tenure (months) *</label>
                <Input
                  type="number"
                  {...register('min_tenure_months', { valueAsNumber: true })}
                  placeholder="12"
                />
                {errors.min_tenure_months && (
                  <p className="text-sm text-red-600 mt-1">{errors.min_tenure_months.message}</p>
                )}
              </div>
              <div>
                <label className="text-sm font-medium mb-1 block">Max Tenure (months) *</label>
                <Input
                  type="number"
                  {...register('max_tenure_months', { valueAsNumber: true })}
                  placeholder="60"
                />
                {errors.max_tenure_months && (
                  <p className="text-sm text-red-600 mt-1">{errors.max_tenure_months.message}</p>
                )}
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Age & Employment */}
        <Card>
          <CardHeader>
            <CardTitle>Age & Employment Rules</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div>
                <label className="text-sm font-medium mb-1 block">Min Age (years) *</label>
                <Input
                  type="number"
                  {...register('min_age', { valueAsNumber: true })}
                  placeholder="21"
                />
                {errors.min_age && (
                  <p className="text-sm text-red-600 mt-1">{errors.min_age.message}</p>
                )}
              </div>
              <div>
                <label className="text-sm font-medium mb-1 block">Max Age (years) *</label>
                <Input
                  type="number"
                  {...register('max_age', { valueAsNumber: true })}
                  placeholder="65"
                />
                {errors.max_age && (
                  <p className="text-sm text-red-600 mt-1">{errors.max_age.message}</p>
                )}
              </div>
              <div>
                <label className="text-sm font-medium mb-1 block">Min Years in Employment *</label>
                <Input
                  type="number"
                  {...register('min_years_in_employment', { valueAsNumber: true })}
                  placeholder="2"
                />
                {errors.min_years_in_employment && (
                  <p className="text-sm text-red-600 mt-1">{errors.min_years_in_employment.message}</p>
                )}
              </div>
            </div>
            <div className="flex items-center gap-2">
              <input
                type="checkbox"
                id="self_employed_allowed"
                {...register('self_employed_allowed')}
                className="h-4 w-4 rounded border-gray-300"
              />
              <label htmlFor="self_employed_allowed" className="text-sm font-medium">Allow Self-Employed</label>
            </div>
          </CardContent>
        </Card>

        {/* Geographic Restrictions */}
        <Card>
          <CardHeader>
            <CardTitle>Geographic Restrictions</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <label className="text-sm font-medium mb-2 block">Allowed States (Leave empty for all)</label>
              <div className="border rounded-md p-3 max-h-40 overflow-y-auto">
                <div className="grid grid-cols-2 md:grid-cols-4 gap-2">
                  {INDIAN_STATES.map(state => (
                    <label key={state} className="flex items-center gap-2 text-sm">
                      <input
                        type="checkbox"
                        checked={selectedStates.includes(state)}
                        onChange={() => toggleItem(state, selectedStates, setSelectedStates)}
                        className="h-4 w-4 rounded border-gray-300"
                      />
                      {state}
                    </label>
                  ))}
                </div>
              </div>
            </div>
            <div>
              <label className="text-sm font-medium mb-2 block">Negative Geographies</label>
              <div className="border rounded-md p-3 max-h-40 overflow-y-auto">
                <div className="grid grid-cols-2 md:grid-cols-4 gap-2">
                  {INDIAN_STATES.map(state => (
                    <label key={state} className="flex items-center gap-2 text-sm">
                      <input
                        type="checkbox"
                        checked={negativeStates.includes(state)}
                        onChange={() => toggleItem(state, negativeStates, setNegativeStates)}
                        className="h-4 w-4 rounded border-gray-300"
                      />
                      {state}
                    </label>
                  ))}
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Negative Profiles */}
        <Card>
          <CardHeader>
            <CardTitle>Negative Profiles</CardTitle>
          </CardHeader>
          <CardContent>
            <label className="text-sm font-medium mb-2 block">Negative Professions</label>
            <div className="flex flex-wrap gap-2">
              {PROFESSIONS.map(profession => (
                <Badge
                  key={profession}
                  variant={negativeProfessions.includes(profession) ? 'destructive' : 'outline'}
                  className="cursor-pointer"
                  onClick={() => toggleItem(profession, negativeProfessions, setNegativeProfessions)}
                >
                  {profession}
                </Badge>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Documentation Requirements */}
        <Card>
          <CardHeader>
            <CardTitle>Documentation Requirements</CardTitle>
          </CardHeader>
          <CardContent>
            <label className="text-sm font-medium mb-2 block">Required Documents</label>
            <div className="flex flex-wrap gap-2">
              {DOCUMENTS.map(doc => (
                <Badge
                  key={doc}
                  variant={selectedDocuments.includes(doc) ? 'default' : 'outline'}
                  className="cursor-pointer"
                  onClick={() => toggleItem(doc, selectedDocuments, setSelectedDocuments)}
                >
                  {doc}
                </Badge>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Actions */}
        <div className="flex justify-end gap-2">
          <Link href="/risk/policies">
            <Button variant="outline" type="button">Cancel</Button>
          </Link>
          <Button type="submit" disabled={createMutation.isPending}>
            <Save className="h-4 w-4 mr-2" />
            {createMutation.isPending ? 'Saving...' : 'Save Policy'}
          </Button>
        </div>
      </form>
    </DashboardLayout>
  )
}
