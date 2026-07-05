'use client'

import { useState, useEffect } from 'react'
import { useMutation, useQuery } from '@tanstack/react-query'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import { ArrowLeft, Loader2, Calculator } from 'lucide-react'
import { DashboardLayout } from '@/components/layout/dashboard-layout'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { useToast } from '@/hooks/use-toast'
import { loanService } from '@/services/loan.service'
import { customerService } from '@/services/customer.service'
import { formatCurrency, calculateEMI } from '@/lib/utils'

export default function NewLoanApplicationPage() {
  const router = useRouter()
  const { toast } = useToast()
  const [formData, setFormData] = useState({
    customer_id: '',
    product_id: '',
    loan_amount: '',
    tenure_months: '',
    purpose: '',
  })
  const [calculatedEMI, setCalculatedEMI] = useState(0)
  const [interestRate, setInterestRate] = useState(12) // Default rate

  // Fetch customers for dropdown
  const { data: customers } = useQuery({
    queryKey: ['customers-list'],
    queryFn: () => customerService.getCustomers({ page: 1, page_size: 100 }),
  })

  // Fetch loan products
  const { data: products } = useQuery({
    queryKey: ['loan-products'],
    queryFn: () => loanService.getProducts({ page: 1, page_size: 50 }),
  })

  // Calculate EMI when amount, tenure, or rate changes
  useEffect(() => {
    const amount = parseFloat(formData.loan_amount)
    const tenure = parseInt(formData.tenure_months)
    
    if (amount > 0 && tenure > 0 && interestRate > 0) {
      const emi = calculateEMI(amount, interestRate, tenure)
      setCalculatedEMI(emi)
    } else {
      setCalculatedEMI(0)
    }
  }, [formData.loan_amount, formData.tenure_months, interestRate])

  const createMutation = useMutation({
    mutationFn: (data: any) => loanService.createApplication(data),
    onSuccess: (response) => {
      toast({
        title: 'Success',
        description: 'Loan application created successfully',
      })
      router.push(`/loans/applications/${response.data?.id}`)
    },
    onError: (error: any) => {
      toast({
        title: 'Error',
        description: error.message || 'Failed to create loan application',
        variant: 'destructive',
      })
    },
  })

  const handleChange = (field: string, value: string) => {
    setFormData(prev => ({ ...prev, [field]: value }))
  }

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    
    // Validation
    if (!formData.customer_id || !formData.product_id || !formData.loan_amount || !formData.tenure_months) {
      toast({
        title: 'Validation Error',
        description: 'Please fill in all required fields',
        variant: 'destructive',
      })
      return
    }

    createMutation.mutate({
      ...formData,
      loan_amount: parseFloat(formData.loan_amount),
      tenure_months: parseInt(formData.tenure_months),
    })
  }

  return (
    <DashboardLayout>
      <form onSubmit={handleSubmit} className="space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <Link href="/loans/applications">
              <Button type="button" variant="ghost" size="icon">
                <ArrowLeft className="h-5 w-5" />
              </Button>
            </Link>
            <div>
              <h1 className="text-3xl font-bold text-gray-900">New Loan Application</h1>
              <p className="text-gray-600 mt-1">Create a new loan application</p>
            </div>
          </div>
          <div className="flex gap-2">
            <Link href="/loans/applications">
              <Button type="button" variant="outline">
                Cancel
              </Button>
            </Link>
            <Button type="submit" disabled={createMutation.isPending}>
              {createMutation.isPending ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Creating...
                </>
              ) : (
                'Create Application'
              )}
            </Button>
          </div>
        </div>

        {/* Customer Selection */}
        <Card>
          <CardHeader>
            <CardTitle>Customer Information</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="customer_id">
                Select Customer <span className="text-red-500">*</span>
              </Label>
              <select
                id="customer_id"
                value={formData.customer_id}
                onChange={(e) => handleChange('customer_id', e.target.value)}
                className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
                required
              >
                <option value="">Select a customer</option>
                {customers?.data?.items?.map((customer: any) => (
                  <option key={customer.id} value={customer.id}>
                    {customer.full_name} - {customer.customer_code}
                  </option>
                ))}
              </select>
              <p className="text-sm text-gray-500">
                Can't find customer? <Link href="/customers/new" className="text-blue-600 hover:underline">Add new customer</Link>
              </p>
            </div>
          </CardContent>
        </Card>

        {/* Loan Details */}
        <Card>
          <CardHeader>
            <CardTitle>Loan Details</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="product_id">
                Loan Product <span className="text-red-500">*</span>
              </Label>
              <select
                id="product_id"
                value={formData.product_id}
                onChange={(e) => handleChange('product_id', e.target.value)}
                className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
                required
              >
                <option value="">Select a product</option>
                {products?.data?.items?.map((product: any) => (
                  <option key={product.id} value={product.id}>
                    {product.product_name} - {product.interest_rate}% p.a.
                  </option>
                ))}
              </select>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="loan_amount">
                  Loan Amount (₹) <span className="text-red-500">*</span>
                </Label>
                <Input
                  id="loan_amount"
                  type="number"
                  value={formData.loan_amount}
                  onChange={(e) => handleChange('loan_amount', e.target.value)}
                  placeholder="Enter loan amount"
                  min="1000"
                  step="1000"
                  required
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="tenure_months">
                  Tenure (Months) <span className="text-red-500">*</span>
                </Label>
                <Input
                  id="tenure_months"
                  type="number"
                  value={formData.tenure_months}
                  onChange={(e) => handleChange('tenure_months', e.target.value)}
                  placeholder="Enter tenure in months"
                  min="1"
                  max="360"
                  required
                />
              </div>
            </div>

            <div className="space-y-2">
              <Label htmlFor="purpose">
                Loan Purpose <span className="text-red-500">*</span>
              </Label>
              <Input
                id="purpose"
                value={formData.purpose}
                onChange={(e) => handleChange('purpose', e.target.value)}
                placeholder="Enter purpose of loan"
                required
              />
            </div>
          </CardContent>
        </Card>

        {/* EMI Calculator */}
        {calculatedEMI > 0 && (
          <Card className="bg-blue-50 border-blue-200">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Calculator className="h-5 w-5" />
                EMI Calculation
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                <div>
                  <p className="text-sm text-gray-600 mb-1">Loan Amount</p>
                  <p className="text-lg font-bold text-gray-900">
                    {formatCurrency(parseFloat(formData.loan_amount))}
                  </p>
                </div>
                <div>
                  <p className="text-sm text-gray-600 mb-1">Interest Rate</p>
                  <p className="text-lg font-bold text-gray-900">
                    {interestRate}% p.a.
                  </p>
                </div>
                <div>
                  <p className="text-sm text-gray-600 mb-1">Tenure</p>
                  <p className="text-lg font-bold text-gray-900">
                    {formData.tenure_months} months
                  </p>
                </div>
                <div>
                  <p className="text-sm text-gray-600 mb-1">Monthly EMI</p>
                  <p className="text-2xl font-bold text-blue-600">
                    {formatCurrency(calculatedEMI)}
                  </p>
                </div>
              </div>

              <div className="mt-6 pt-6 border-t border-blue-200">
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div>
                    <p className="text-sm text-gray-600 mb-1">Total Payable</p>
                    <p className="text-lg font-semibold text-gray-900">
                      {formatCurrency(calculatedEMI * parseInt(formData.tenure_months))}
                    </p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-600 mb-1">Total Interest</p>
                    <p className="text-lg font-semibold text-gray-900">
                      {formatCurrency((calculatedEMI * parseInt(formData.tenure_months)) - parseFloat(formData.loan_amount))}
                    </p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-600 mb-1">Interest %</p>
                    <p className="text-lg font-semibold text-gray-900">
                      {(((calculatedEMI * parseInt(formData.tenure_months)) - parseFloat(formData.loan_amount)) / parseFloat(formData.loan_amount) * 100).toFixed(2)}%
                    </p>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        )}

        {/* Info Box */}
        <Card className="bg-gray-50">
          <CardContent className="pt-6">
            <h3 className="font-semibold text-gray-900 mb-2">Important Notes</h3>
            <ul className="list-disc list-inside space-y-1 text-sm text-gray-600">
              <li>Application will be created in Draft status</li>
              <li>You can edit the application before submission</li>
              <li>Submit the application to start the approval process</li>
              <li>All required documents must be uploaded before disbursement</li>
            </ul>
          </CardContent>
        </Card>
      </form>
    </DashboardLayout>
  )
}
