'use client'

import { useState, useEffect } from 'react'
import { useRouter, useSearchParams } from 'next/navigation'
import { salesApi, OrderCreate, OrderUpdate, Order, OrderItemCreate, Product, Quote } from '@/services/salesApi'
import { crmApi, CRMAccount } from '@/services/crmApi'

interface OrderFormProps {
  orderId?: string
  mode: 'create' | 'edit'
}

export default function OrderForm({ orderId, mode }: OrderFormProps) {
  const router = useRouter()
  const searchParams = useSearchParams()
  const quoteId = searchParams?.get('quote')
  
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [success, setSuccess] = useState<string | null>(null)

  // Data
  const [accounts, setAccounts] = useState<CRMAccount[]>([])
  const [products, setProducts] = useState<Product[]>([])
  const [loadingData, setLoadingData] = useState(true)

  // Form state
  const [formData, setFormData] = useState({
    account_id: '',
    quote_id: quoteId || '',
    order_date: new Date().toISOString().split('T')[0],
    expected_delivery_date: new Date(Date.now() + 7 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
    currency: 'INR',
    subtotal: 0,
    discount_percentage: 0,
    discount_amount: 0,
    tax_amount: 0,
    total_amount: 0,
    paid_amount: 0,
    payment_status: 'unpaid' as 'paid' | 'partial' | 'unpaid',
    payment_method: '',
    shipping_address: '',
    billing_address: '',
    terms_conditions: '',
    notes: '',
    status: 'pending' as any,
  })

  const [items, setItems] = useState<OrderItemCreate[]>([])

  useEffect(() => {
    loadInitialData()
  }, [])

  useEffect(() => {
    if (mode === 'edit' && orderId) {
      loadOrder()
    } else if (mode === 'create' && quoteId) {
      loadQuoteData()
    }
  }, [orderId, quoteId, mode])

  useEffect(() => {
    calculateTotals()
  }, [items, formData.discount_percentage, formData.discount_amount])

  const loadInitialData = async () => {
    try {
      setLoadingData(true)
      const [accountsRes, productsRes] = await Promise.all([
        crmApi.accounts.list({ limit: 1000 }),
        salesApi.products.list({ limit: 1000, status: 'active' }),
      ])

      if (accountsRes.success) {
        setAccounts(accountsRes.data.accounts)
      }
      if (productsRes.success) {
        setProducts(productsRes.data.products)
      }
    } catch (err: any) {
      setError('Failed to load initial data')
    } finally {
      setLoadingData(false)
    }
  }

  const loadQuoteData = async () => {
    if (!quoteId) return

    try {
      const response = await salesApi.quotes.get(quoteId)
      if (response.success) {
        const quote = response.data
        setFormData(prev => ({
          ...prev,
          account_id: quote.account_id,
          quote_id: quoteId,
          currency: quote.currency,
          subtotal: quote.subtotal,
          discount_percentage: quote.discount_percentage || 0,
          discount_amount: quote.discount_amount,
          tax_amount: quote.tax_amount,
          total_amount: quote.total_amount,
          terms_conditions: quote.terms_conditions || '',
        }))
        setItems(quote.items || [])
      }
    } catch (err: any) {
      setError('Failed to load quote data')
    }
  }

  const loadOrder = async () => {
    if (!orderId) return

    try {
      setLoading(true)
      const response = await salesApi.orders.get(orderId)

      if (response.success) {
        const order = response.data
        setFormData({
          account_id: order.account_id,
          quote_id: order.quote_id || '',
          order_date: order.order_date.split('T')[0],
          expected_delivery_date: order.expected_delivery_date?.split('T')[0] || '',
          currency: order.currency,
          subtotal: order.subtotal,
          discount_percentage: order.discount_percentage || 0,
          discount_amount: order.discount_amount,
          tax_amount: order.tax_amount,
          total_amount: order.total_amount,
          paid_amount: order.paid_amount,
          payment_status: order.payment_status,
          payment_method: order.payment_method || '',
          shipping_address: order.shipping_address || '',
          billing_address: order.billing_address || '',
          terms_conditions: order.terms_conditions || '',
          notes: order.notes || '',
          status: order.status,
        })
        setItems(order.items || [])
      } else {
        setError('Failed to load order')
      }
    } catch (err: any) {
      setError(err.message || 'Failed to load order')
    } finally {
      setLoading(false)
    }
  }

  const calculateTotals = () => {
    const subtotal = items.reduce((sum, item) => sum + item.line_total, 0)
    
    let discountAmount = formData.discount_amount
    if (formData.discount_percentage > 0) {
      discountAmount = (subtotal * formData.discount_percentage) / 100
    }

    const taxAmount = items.reduce((sum, item) => sum + item.tax_amount, 0)
    const totalAmount = subtotal - discountAmount + taxAmount

    // Determine payment status
    let paymentStatus: 'paid' | 'partial' | 'unpaid' = 'unpaid'
    if (formData.paid_amount >= totalAmount) {
      paymentStatus = 'paid'
    } else if (formData.paid_amount > 0) {
      paymentStatus = 'partial'
    }

    setFormData(prev => ({
      ...prev,
      subtotal,
      discount_amount: discountAmount,
      tax_amount: taxAmount,
      total_amount: totalAmount,
      payment_status: paymentStatus,
    }))
  }

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
    const { name, value } = e.target
    setFormData(prev => ({ ...prev, [name]: value }))
  }

  const handlePaidAmountChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = parseFloat(e.target.value) || 0
    setFormData(prev => ({ ...prev, paid_amount: value }))
  }

  const addItem = () => {
    setItems([...items, {
      product_id: '',
      product_name: '',
      description: '',
      quantity: 1,
      unit_price: 0,
      discount_percentage: 0,
      discount_amount: 0,
      tax_rate: 0,
      tax_amount: 0,
      line_total: 0,
    }])
  }

  const removeItem = (index: number) => {
    setItems(items.filter((_, i) => i !== index))
  }

  const updateItem = (index: number, field: keyof OrderItemCreate, value: any) => {
    const newItems = [...items]
    newItems[index] = { ...newItems[index], [field]: value }

    // Auto-calculate when product is selected
    if (field === 'product_id' && value) {
      const product = products.find(p => p.id === value)
      if (product) {
        newItems[index].product_name = product.name
        newItems[index].description = product.description || ''
        newItems[index].unit_price = product.unit_price
        newItems[index].tax_rate = product.tax_rate || 0
      }
    }

    // Calculate line total
    const item = newItems[index]
    const baseAmount = item.quantity * item.unit_price
    let discountAmount = item.discount_amount
    if (item.discount_percentage > 0) {
      discountAmount = (baseAmount * item.discount_percentage) / 100
    }
    const taxableAmount = baseAmount - discountAmount
    const taxAmount = (taxableAmount * item.tax_rate) / 100
    const lineTotal = taxableAmount + taxAmount

    newItems[index].discount_amount = discountAmount
    newItems[index].tax_amount = taxAmount
    newItems[index].line_total = lineTotal

    setItems(newItems)
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    
    if (items.length === 0) {
      setError('Please add at least one item')
      return
    }

    setLoading(true)
    setError(null)
    setSuccess(null)

    try {
      const orderData: OrderCreate = {
        ...formData,
        items,
      }

      if (mode === 'create') {
        const response = await salesApi.orders.create(orderData)
        if (response.success) {
          setSuccess('Order created successfully!')
          setTimeout(() => {
            router.push(`/crm/orders/${response.data.id}`)
          }, 1500)
        } else {
          setError('Failed to create order')
        }
      } else if (mode === 'edit' && orderId) {
        const updateData: OrderUpdate = { ...orderData }
        const response = await salesApi.orders.update(orderId, updateData)
        if (response.success) {
          setSuccess('Order updated successfully!')
          setTimeout(() => {
            router.push(`/crm/orders/${orderId}`)
          }, 1500)
        } else {
          setError('Failed to update order')
        }
      }
    } catch (err: any) {
      setError(err.message || 'Failed to save order')
    } finally {
      setLoading(false)
    }
  }

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: formData.currency,
    }).format(amount)
  }

  if (loadingData) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="mb-6">
          <button
            onClick={() => router.back()}
            className="text-blue-600 hover:text-blue-700 mb-4 flex items-center"
          >
            ← Back
          </button>
          <h1 className="text-3xl font-bold text-gray-900">
            {mode === 'create' ? 'Create New Order' : 'Edit Order'}
          </h1>
          <p className="text-gray-600 mt-1">
            {mode === 'create' 
              ? quoteId ? 'Create order from accepted quote' : 'Create a new customer order' 
              : 'Update order details'}
          </p>
        </div>

        {/* Error/Success Messages */}
        {error && (
          <div className="mb-6 bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg">
            {error}
          </div>
        )}
        {success && (
          <div className="mb-6 bg-green-50 border border-green-200 text-green-700 px-4 py-3 rounded-lg">
            {success}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Order Header */}
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">Order Information</h2>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Account <span className="text-red-500">*</span>
                </label>
                <select
                  name="account_id"
                  value={formData.account_id}
                  onChange={handleChange}
                  required
                  disabled={!!quoteId}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:bg-gray-100"
                >
                  <option value="">Select Account</option>
                  {accounts.map(account => (
                    <option key={account.id} value={account.id}>
                      {account.account_name}
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Order Date <span className="text-red-500">*</span>
                </label>
                <input
                  type="date"
                  name="order_date"
                  value={formData.order_date}
                  onChange={handleChange}
                  required
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Expected Delivery
                </label>
                <input
                  type="date"
                  name="expected_delivery_date"
                  value={formData.expected_delivery_date}
                  onChange={handleChange}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Currency <span className="text-red-500">*</span>
                </label>
                <select
                  name="currency"
                  value={formData.currency}
                  onChange={handleChange}
                  required
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="INR">INR - Indian Rupee</option>
                  <option value="USD">USD - US Dollar</option>
                  <option value="EUR">EUR - Euro</option>
                  <option value="GBP">GBP - British Pound</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Status <span className="text-red-500">*</span>
                </label>
                <select
                  name="status"
                  value={formData.status}
                  onChange={handleChange}
                  required
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="pending">Pending</option>
                  <option value="confirmed">Confirmed</option>
                  <option value="processing">Processing</option>
                  <option value="shipped">Shipped</option>
                  <option value="delivered">Delivered</option>
                  <option value="cancelled">Cancelled</option>
                  <option value="refunded">Refunded</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Payment Method
                </label>
                <input
                  type="text"
                  name="payment_method"
                  value={formData.payment_method}
                  onChange={handleChange}
                  placeholder="e.g., Credit Card, Bank Transfer"
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
            </div>
          </div>

          {/* Order Items - Reuse same structure as QuoteBuilder */}
          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-xl font-semibold text-gray-900">Order Items</h2>
              {!quoteId && (
                <button
                  type="button"
                  onClick={addItem}
                  className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors text-sm"
                >
                  + Add Item
                </button>
              )}
            </div>

            <div className="space-y-4">
              {items.map((item, index) => (
                <div key={index} className="border border-gray-200 rounded-lg p-4">
                  <div className="grid grid-cols-12 gap-4">
                    <div className="col-span-12 md:col-span-4">
                      <label className="block text-sm font-medium text-gray-700 mb-1">Product</label>
                      <select
                        value={item.product_id}
                        onChange={(e) => updateItem(index, 'product_id', e.target.value)}
                        disabled={!!quoteId}
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:bg-gray-100"
                      >
                        <option value="">Select Product</option>
                        {products.map(product => (
                          <option key={product.id} value={product.id}>
                            {product.name} - {formatCurrency(product.unit_price)}
                          </option>
                        ))}
                      </select>
                    </div>

                    <div className="col-span-6 md:col-span-2">
                      <label className="block text-sm font-medium text-gray-700 mb-1">Qty</label>
                      <input
                        type="number"
                        value={item.quantity}
                        onChange={(e) => updateItem(index, 'quantity', parseFloat(e.target.value) || 1)}
                        min="1"
                        step="1"
                        disabled={!!quoteId}
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:bg-gray-100"
                      />
                    </div>

                    <div className="col-span-6 md:col-span-2">
                      <label className="block text-sm font-medium text-gray-700 mb-1">Unit Price</label>
                      <input
                        type="number"
                        value={item.unit_price}
                        onChange={(e) => updateItem(index, 'unit_price', parseFloat(e.target.value) || 0)}
                        min="0"
                        step="0.01"
                        disabled={!!quoteId}
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:bg-gray-100"
                      />
                    </div>

                    <div className="col-span-6 md:col-span-2">
                      <label className="block text-sm font-medium text-gray-700 mb-1">Disc %</label>
                      <input
                        type="number"
                        value={item.discount_percentage}
                        readOnly
                        className="w-full px-3 py-2 bg-gray-50 border border-gray-300 rounded-lg"
                      />
                    </div>

                    <div className="col-span-5 md:col-span-2 flex items-end">
                      <div className="w-full">
                        <label className="block text-sm font-medium text-gray-700 mb-1">Total</label>
                        <div className="px-3 py-2 bg-gray-50 border border-gray-300 rounded-lg text-sm font-medium">
                          {formatCurrency(item.line_total)}
                        </div>
                      </div>
                    </div>

                    {!quoteId && (
                      <div className="col-span-1 flex items-end">
                        <button
                          type="button"
                          onClick={() => removeItem(index)}
                          className="p-2 text-red-600 hover:bg-red-50 rounded-lg transition-colors"
                        >
                          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                          </svg>
                        </button>
                      </div>
                    )}
                  </div>
                </div>
              ))}

              {items.length === 0 && (
                <div className="text-center py-8 text-gray-500">
                  No items added. Click "Add Item" to start building your order.
                </div>
              )}
            </div>
          </div>

          {/* Payment & Totals */}
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">Payment & Totals</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Amount Paid
                </label>
                <input
                  type="number"
                  value={formData.paid_amount}
                  onChange={handlePaidAmountChange}
                  min="0"
                  step="0.01"
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
                <p className="text-xs text-gray-500 mt-1">
                  Balance: {formatCurrency(formData.total_amount - formData.paid_amount)}
                </p>
              </div>

              <div className="bg-gray-50 rounded-lg p-4 space-y-2">
                <div className="flex justify-between text-sm">
                  <span className="text-gray-600">Subtotal:</span>
                  <span className="font-medium">{formatCurrency(formData.subtotal)}</span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-gray-600">Discount:</span>
                  <span className="font-medium text-red-600">-{formatCurrency(formData.discount_amount)}</span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-gray-600">Tax:</span>
                  <span className="font-medium">{formatCurrency(formData.tax_amount)}</span>
                </div>
                <div className="flex justify-between text-lg font-bold pt-2 border-t">
                  <span>Total:</span>
                  <span className="text-blue-600">{formatCurrency(formData.total_amount)}</span>
                </div>
                <div className="flex justify-between text-sm pt-2 border-t">
                  <span className="text-gray-600">Payment Status:</span>
                  <span className={`font-medium ${formData.payment_status === 'paid' ? 'text-green-600' : formData.payment_status === 'partial' ? 'text-yellow-600' : 'text-red-600'}`}>
                    {formData.payment_status.toUpperCase()}
                  </span>
                </div>
              </div>
            </div>
          </div>

          {/* Addresses & Notes */}
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">Additional Information</h2>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Shipping Address</label>
                <textarea
                  name="shipping_address"
                  value={formData.shipping_address}
                  onChange={handleChange}
                  rows={3}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="Enter shipping address..."
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Billing Address</label>
                <textarea
                  name="billing_address"
                  value={formData.billing_address}
                  onChange={handleChange}
                  rows={3}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="Enter billing address..."
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Internal Notes</label>
                <textarea
                  name="notes"
                  value={formData.notes}
                  onChange={handleChange}
                  rows={3}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="Internal notes..."
                />
              </div>
            </div>
          </div>

          {/* Form Actions */}
          <div className="flex gap-4 justify-end">
            <button
              type="button"
              onClick={() => router.back()}
              className="px-6 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={loading}
              className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              {loading ? 'Saving...' : mode === 'create' ? 'Create Order' : 'Update Order'}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}
