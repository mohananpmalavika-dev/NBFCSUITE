'use client'

import { useState, useEffect } from 'react'
import { useMutation, useQuery } from '@tanstack/react-query'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import { ArrowLeft, Loader2, Info } from 'lucide-react'
import { DashboardLayout } from '@/components/layout/dashboard-layout'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { useToast } from '@/hooks/use-toast'
import { depositService } from '@/services/deposit.service'
import { customerService } from '@/services/customer.service'
import { formatCurrency } from '@/lib/utils'
import { DEPOSIT_TYPE_OPTIONS } from '@/lib/constants'

export default function NewDepositAccountPage() {
  const router = useRouter()
  const { toast } = useToast()
  const [formData, setFormData] = useState({
    customer_id: '',
    product_id: '',
    deposit_amount: '',
    tenure_months: '',
  })
  const [selectedProduct, setSelectedProduct] = useState<any>(null)
  const [calculatedMaturity, setCalculatedMaturity] = useState(0)

  // Fetch customers
  const { data: customers } = useQuery({
    queryKey: ['customers-list'],
    queryFn: () => customerService.getCustomers({ page: 1, page_size: 100 }),
  })

  // Fetch deposit products
  const { data: products } = useQuery({
    queryKey: ['deposit-products'],
    queryFn: () => depositService.getProducts({ page: 1, page_size: 50 }),
  })

  // Calculate maturity amount for FD/RD
  useEffect(() => {
    if (selectedProduct && formData.deposit_amount && formData.tenure_months) {
      const amount = parseFloat(formData.deposit_amount)
      const tenure = parseInt(formData.tenure_months)
      const rate = selectedProduct.interest_rate

      if (amount > 0 && tenure > 0 && rate > 0) {
        // Simple interest calculation for demo
        const interest = (amount * rate * tenure) / (12 * 100)
        setCalculatedMaturity(amount + interest)
      } else {
        setCalculatedMaturity(0)
      }
    }
  }, [formData.deposit_amount, formData.tenure_months, selectedProduct])

  const createMutation = useMutation({
    mutationFn: (data: any) => depositService.createAccount(data),
    onSuccess: (response) => {
      toast({
        title: 'Success',
        description: 'Deposit account opened successfully',
      })
      router.push(`/deposits/accounts/${response.data?.id}`)
    },
    onError: (error: any) => {
      toast({
        title: 'Error',
        description: error.message || 'Failed to open deposit account',
        variant: 'destructive',
      })
    },
  })

  const handleChange = (field: string, value: string) => {
    setFormData(prev => ({ ...prev, [field]: value }))
    
    // Update selected product when product changes
    if (field === 'product_id' && products?.data?.items) {
      const product = products.data.items.find((p: any) => p.id === value)
      setSelectedProduct(product)
    }
  }

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    
    // Validation
    if (!formData.customer_id || !formData.product_id || !formData.deposit_amount) {
      toast({
        title: 'Validation Error',
        description: 'Please fill in all required fields',
        variant: 'destructive',
      })
      return
    }

    createMutation.mutate({
      ...formData,
      deposit_amount: parseFloat(formData.deposit_amount),
      tenure_months: formData.tenure_months ? parseInt(formData.tenure_months) : undefined,
    })
  }

  return (
    <DashboardLayout>
      <form onSubmit={handleSubmit} className="space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <Link href="/deposits/accounts">
              <Button type="button" variant="ghost" size="icon">
                <ArrowLeft className="h-5 w-5" />
              </Button>
            </Link>
            <div>
              <h1 className="text-3xl font-bold text-gray-900">Open Deposit Account</h1>
              <p className="text-gray-600 mt-1">Create a new deposit account</p>
            </div>
          </div>
          <div className="flex gap-2">
            <Link href="/deposits/accounts">
              <Button type="button" variant="outline">
                Cancel
              </Button>
            </Link>
            <Button type="submit" disabled={createMutation.isPending}>
              {createMutation.isPending ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Opening...
                </>
              ) : (
                'Open Account'
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

        {/* Product Selection */}
        <Card>
          <CardHeader>
            <CardTitle>Deposit Product</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="product_id">
                Select Product <span className="text-red-500">*</span>
              </Label>
              <select
                id="product_id"
                value={formData.product_id}
                onChange={(e) => handleChange('product_id', e.target.value)}
                className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
                required
              >
                <option value="">Select a deposit product</option>
                {products?.data?.items?.map((product: any) => (
                  <option key={product.id} value={product.id}>
                    {product.product_name} - {product.deposit_type} ({product.interest_rate}% p.a.)
                  </option>
                ))}
              </select>
            </div>

            {selectedProduct && (
              <div className="mt-4 p-4 bg-blue-50 rounded-lg border border-blue-200">
                <h4 className="font-semibold text-gray-900 mb-2">Product Details</h4>
                <div className="grid grid-cols-2 gap-4 text-sm">
                  <div>
                    <p className="text-gray-600">Type</p>
                    <p className="font-medium">{selectedProduct.deposit_type}</p>
                  </div>
                  <div>
                    <p className="text-gray-600">Interest Rate</p>
                    <p className="font-medium">{selectedProduct.interest_rate}% p.a.</p>
                  </div>
                  <div>
                    <p className="text-gray-600">Min Amount</p>
                    <p className="font-medium">{formatCurrency(selectedProduct.min_amount)}</p>
                  </div>
                  {selectedProduct.max_amount && (
                    <div>
                      <p className="text-gray-600">Max Amount</p>
                      <p className="font-medium">{formatCurrency(selectedProduct.max_amount)}</p>
                    </div>
                  )}
                </div>
              </div>
            )}
          </CardContent>
        </Card>

        {/* Deposit Details */}
        <Card>
          <CardHeader>
            <CardTitle>Deposit Details</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="deposit_amount">
                  Deposit Amount (₹) <span className="text-red-500">*</span>
                </Label>
                <Input
                  id="deposit_amount"
                  type="number"
                  value={formData.deposit_amount}
                  onChange={(e) => handleChange('deposit_amount', e.target.value)}
                  placeholder="Enter deposit amount"
                  min={selectedProduct?.min_amount || 1000}
                  max={selectedProduct?.max_amount}
                  step="100"
                  required
                />
                {selectedProduct && (
                  <p className="text-xs text-gray-500">
                    Min: {formatCurrency(selectedProduct.min_amount)}
                    {selectedProduct.max_amount && ` - Max: ${formatCurrency(selectedProduct.max_amount)}`}
                  </p>
                )}
              </div>

              {selectedProduct && selectedProduct.deposit_type !== 'Savings' && (
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
                    min={selectedProduct.min_tenure_months || 1}
                    max={selectedProduct.max_tenure_months || 120}
                    required
                  />
                  <p className="text-xs text-gray-500">
                    {selectedProduct.min_tenure_months && `Min: ${selectedProduct.min_tenure_months} months`}
                    {selectedProduct.max_tenure_months && ` - Max: ${selectedProduct.max_tenure_months} months`}
                  </p>
                </div>
              )}
            </div>
          </CardContent>
        </Card>

        {/* Maturity Calculation */}
        {calculatedMaturity > 0 && selectedProduct.deposit_type !== 'Savings' && (
          <Card className="bg-green-50 border-green-200">
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-green-900">
                <Info className="h-5 w-5" />
                Maturity Calculation
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div>
                  <p className="text-sm text-gray-600 mb-1">Deposit Amount</p>
                  <p className="text-lg font-bold text-gray-900">
                    {formatCurrency(parseFloat(formData.deposit_amount))}
                  </p>
                </div>
                <div>
                  <p className="text-sm text-gray-600 mb-1">Interest Earned</p>
                  <p className="text-lg font-bold text-green-600">
                    {formatCurrency(calculatedMaturity - parseFloat(formData.deposit_amount))}
                  </p>
                </div>
                <div>
                  <p className="text-sm text-gray-600 mb-1">Maturity Amount</p>
                  <p className="text-2xl font-bold text-green-700">
                    {formatCurrency(calculatedMaturity)}
                  </p>
                </div>
              </div>
              <p className="text-xs text-gray-600 mt-4">
                * This is an estimated calculation. Actual maturity amount may vary based on interest calculation method.
              </p>
            </CardContent>
          </Card>
        )}

        {/* Info Box */}
        <Card className="bg-gray-50">
          <CardContent className="pt-6">
            <h3 className="font-semibold text-gray-900 mb-2">Important Information</h3>
            <ul className="list-disc list-inside space-y-1 text-sm text-gray-600">
              <li>Account will be created in Active status</li>
              <li>Interest will be calculated based on the product's interest rate</li>
              <li>For Fixed and Recurring Deposits, tenure is mandatory</li>
              <li>Premature withdrawal may attract penalties</li>
              <li>All transactions will be recorded in the account statement</li>
            </ul>
          </CardContent>
        </Card>
      </form>
    </DashboardLayout>
  )
}
