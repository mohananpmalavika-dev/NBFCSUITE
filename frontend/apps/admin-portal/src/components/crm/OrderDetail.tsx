'use client'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import { salesApi, Order } from '@/services/salesApi'

interface OrderDetailProps {
  orderId: string
}

export default function OrderDetail({ orderId }: OrderDetailProps) {
  const router = useRouter()
  const [order, setOrder] = useState<Order | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    loadOrder()
  }, [orderId])

  const loadOrder = async () => {
    try {
      setLoading(true)
      setError(null)

      const response = await salesApi.orders.get(orderId)

      if (response.success) {
        setOrder(response.data)
      } else {
        setError('Failed to load order')
      }
    } catch (err: any) {
      setError(err.message || 'Failed to load order')
    } finally {
      setLoading(false)
    }
  }

  const handleDelete = async () => {
    if (!order) return

    if (!confirm(`Are you sure you want to delete order "${order.order_number}"?`)) {
      return
    }

    try {
      await salesApi.orders.delete(orderId)
      router.push('/crm/orders')
    } catch (err: any) {
      alert(err.message || 'Failed to delete order')
    }
  }

  const getStatusBadgeColor = (status: string) => {
    switch (status) {
      case 'pending':
        return 'bg-yellow-100 text-yellow-800'
      case 'confirmed':
        return 'bg-blue-100 text-blue-800'
      case 'processing':
        return 'bg-purple-100 text-purple-800'
      case 'shipped':
        return 'bg-indigo-100 text-indigo-800'
      case 'delivered':
        return 'bg-green-100 text-green-800'
      case 'cancelled':
        return 'bg-red-100 text-red-800'
      case 'refunded':
        return 'bg-orange-100 text-orange-800'
      default:
        return 'bg-gray-100 text-gray-800'
    }
  }

  const getPaymentStatusBadge = (status: string) => {
    switch (status) {
      case 'paid':
        return 'bg-green-100 text-green-800'
      case 'partial':
        return 'bg-yellow-100 text-yellow-800'
      case 'unpaid':
        return 'bg-red-100 text-red-800'
      default:
        return 'bg-gray-100 text-gray-800'
    }
  }

  const formatCurrency = (amount: number, currency: string = 'INR') => {
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: currency,
    }).format(amount)
  }

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-IN', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
    })
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading order...</p>
        </div>
      </div>
    )
  }

  if (error || !order) {
    return (
      <div className="min-h-screen bg-gray-50 p-6">
        <div className="max-w-4xl mx-auto">
          <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg">
            {error || 'Order not found'}
          </div>
          <button
            onClick={() => router.push('/crm/orders')}
            className="mt-4 text-blue-600 hover:text-blue-700"
          >
            ← Back to Orders
          </button>
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
            onClick={() => router.push('/crm/orders')}
            className="text-blue-600 hover:text-blue-700 mb-4 flex items-center"
          >
            ← Back to Orders
          </button>

          <div className="flex justify-between items-start">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">{order.order_number}</h1>
              <p className="text-gray-600 mt-1">Order Details</p>
            </div>

            <div className="flex gap-2">
              <button
                onClick={() => router.push(`/crm/orders/${orderId}/edit`)}
                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
              >
                Edit Order
              </button>
              <button
                onClick={handleDelete}
                className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors"
              >
                Delete
              </button>
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Main Content */}
          <div className="lg:col-span-2 space-y-6">
            {/* Order Document */}
            <div className="bg-white rounded-lg shadow p-8">
              {/* Header */}
              <div className="border-b pb-6 mb-6">
                <div className="flex justify-between items-start">
                  <div>
                    <h2 className="text-2xl font-bold text-gray-900 mb-2">ORDER CONFIRMATION</h2>
                    <p className="text-sm text-gray-600">Order #: {order.order_number}</p>
                    {order.quote_id && (
                      <p className="text-sm text-gray-600">Created from Quote</p>
                    )}
                  </div>
                  <div className="text-right">
                    <span className={`inline-block text-sm px-3 py-1 rounded-full mb-2 ${getStatusBadgeColor(order.status)}`}>
                      {order.status.toUpperCase()}
                    </span>
                    <br />
                    <span className={`inline-block text-sm px-3 py-1 rounded-full ${getPaymentStatusBadge(order.payment_status)}`}>
                      {order.payment_status.toUpperCase()}
                    </span>
                  </div>
                </div>
              </div>

              {/* Customer & Dates */}
              <div className="grid grid-cols-2 gap-6 mb-6">
                <div>
                  <h3 className="text-sm font-semibold text-gray-700 mb-2">CUSTOMER</h3>
                  <p className="text-gray-900 font-medium">{order.account_name}</p>
                </div>
                <div>
                  <h3 className="text-sm font-semibold text-gray-700 mb-2">DATES</h3>
                  <p className="text-sm text-gray-600">Order Date: {formatDate(order.order_date)}</p>
                  {order.expected_delivery_date && (
                    <p className="text-sm text-gray-600">Expected Delivery: {formatDate(order.expected_delivery_date)}</p>
                  )}
                  {order.delivery_date && (
                    <p className="text-sm text-gray-600">Delivered: {formatDate(order.delivery_date)}</p>
                  )}
                </div>
              </div>

              {/* Addresses */}
              {(order.shipping_address || order.billing_address) && (
                <div className="grid grid-cols-2 gap-6 mb-6">
                  {order.shipping_address && (
                    <div>
                      <h3 className="text-sm font-semibold text-gray-700 mb-2">SHIPPING ADDRESS</h3>
                      <p className="text-sm text-gray-900 whitespace-pre-wrap">{order.shipping_address}</p>
                    </div>
                  )}
                  {order.billing_address && (
                    <div>
                      <h3 className="text-sm font-semibold text-gray-700 mb-2">BILLING ADDRESS</h3>
                      <p className="text-sm text-gray-900 whitespace-pre-wrap">{order.billing_address}</p>
                    </div>
                  )}
                </div>
              )}

              {/* Items Table */}
              <div className="mb-6">
                <table className="w-full">
                  <thead className="bg-gray-50 border-t border-b">
                    <tr>
                      <th className="text-left py-3 px-4 text-xs font-semibold text-gray-700 uppercase">Item</th>
                      <th className="text-right py-3 px-4 text-xs font-semibold text-gray-700 uppercase">Qty</th>
                      <th className="text-right py-3 px-4 text-xs font-semibold text-gray-700 uppercase">Price</th>
                      <th className="text-right py-3 px-4 text-xs font-semibold text-gray-700 uppercase">Disc</th>
                      <th className="text-right py-3 px-4 text-xs font-semibold text-gray-700 uppercase">Tax</th>
                      <th className="text-right py-3 px-4 text-xs font-semibold text-gray-700 uppercase">Total</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y">
                    {order.items?.map((item, index) => (
                      <tr key={index}>
                        <td className="py-3 px-4">
                          <p className="text-sm font-medium text-gray-900">{item.product_name}</p>
                          {item.description && (
                            <p className="text-xs text-gray-600 mt-1">{item.description}</p>
                          )}
                        </td>
                        <td className="text-right py-3 px-4 text-sm text-gray-900">{item.quantity}</td>
                        <td className="text-right py-3 px-4 text-sm text-gray-900">
                          {formatCurrency(item.unit_price, order.currency)}
                        </td>
                        <td className="text-right py-3 px-4 text-sm text-red-600">
                          {item.discount_amount > 0 ? `-${formatCurrency(item.discount_amount, order.currency)}` : '-'}
                        </td>
                        <td className="text-right py-3 px-4 text-sm text-gray-900">
                          {formatCurrency(item.tax_amount, order.currency)}
                        </td>
                        <td className="text-right py-3 px-4 text-sm font-medium text-gray-900">
                          {formatCurrency(item.line_total, order.currency)}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>

              {/* Totals */}
              <div className="flex justify-end">
                <div className="w-64 space-y-2">
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-600">Subtotal:</span>
                    <span className="font-medium">{formatCurrency(order.subtotal, order.currency)}</span>
                  </div>
                  {order.discount_amount > 0 && (
                    <div className="flex justify-between text-sm">
                      <span className="text-gray-600">
                        Discount {order.discount_percentage > 0 ? `(${order.discount_percentage}%)` : ''}:
                      </span>
                      <span className="font-medium text-red-600">
                        -{formatCurrency(order.discount_amount, order.currency)}
                      </span>
                    </div>
                  )}
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-600">Tax:</span>
                    <span className="font-medium">{formatCurrency(order.tax_amount, order.currency)}</span>
                  </div>
                  <div className="flex justify-between text-lg font-bold pt-2 border-t">
                    <span>Total:</span>
                    <span className="text-blue-600">{formatCurrency(order.total_amount, order.currency)}</span>
                  </div>
                  <div className="flex justify-between text-sm pt-2 border-t">
                    <span className="text-gray-600">Amount Paid:</span>
                    <span className="font-medium text-green-600">{formatCurrency(order.paid_amount, order.currency)}</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-600">Balance Due:</span>
                    <span className="font-medium text-red-600">
                      {formatCurrency(order.total_amount - order.paid_amount, order.currency)}
                    </span>
                  </div>
                </div>
              </div>

              {/* Payment Method */}
              {order.payment_method && (
                <div className="mt-6 pt-6 border-t">
                  <p className="text-sm text-gray-600">
                    <span className="font-semibold">Payment Method:</span> {order.payment_method}
                  </p>
                </div>
              )}
            </div>

            {/* Internal Notes */}
            {order.notes && (
              <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-2">Internal Notes</h3>
                <p className="text-sm text-gray-700 whitespace-pre-wrap">{order.notes}</p>
              </div>
            )}

            {/* Tracking Info */}
            {order.tracking_number && (
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-2">Shipping Information</h3>
                <p className="text-sm text-gray-700">
                  <span className="font-medium">Tracking Number:</span> {order.tracking_number}
                </p>
                {order.shipped_date && (
                  <p className="text-sm text-gray-700 mt-1">
                    <span className="font-medium">Shipped Date:</span> {formatDate(order.shipped_date)}
                  </p>
                )}
              </div>
            )}
          </div>

          {/* Sidebar */}
          <div className="space-y-6">
            {/* Quick Info */}
            <div className="bg-white rounded-lg shadow p-6">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">Quick Info</h2>
              <div className="space-y-4">
                <div>
                  <p className="text-sm text-gray-600">Order Status</p>
                  <span className={`inline-block mt-1 text-sm px-3 py-1 rounded-full ${getStatusBadgeColor(order.status)}`}>
                    {order.status.toUpperCase()}
                  </span>
                </div>

                <div>
                  <p className="text-sm text-gray-600">Payment Status</p>
                  <span className={`inline-block mt-1 text-sm px-3 py-1 rounded-full ${getPaymentStatusBadge(order.payment_status)}`}>
                    {order.payment_status.toUpperCase()}
                  </span>
                </div>

                <div>
                  <p className="text-sm text-gray-600">Customer</p>
                  <p className="text-sm text-gray-900 mt-1 font-medium">{order.account_name}</p>
                </div>

                <div>
                  <p className="text-sm text-gray-600">Order Date</p>
                  <p className="text-sm text-gray-900 mt-1">{formatDate(order.order_date)}</p>
                </div>

                {order.expected_delivery_date && (
                  <div>
                    <p className="text-sm text-gray-600">Expected Delivery</p>
                    <p className="text-sm text-gray-900 mt-1">{formatDate(order.expected_delivery_date)}</p>
                  </div>
                )}

                <div>
                  <p className="text-sm text-gray-600">Currency</p>
                  <p className="text-sm text-gray-900 mt-1">{order.currency}</p>
                </div>

                <div>
                  <p className="text-sm text-gray-600">Total Items</p>
                  <p className="text-sm text-gray-900 mt-1">{order.items?.length || 0}</p>
                </div>
              </div>
            </div>

            {/* Payment Summary */}
            <div className="bg-white rounded-lg shadow p-6">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">Payment Summary</h2>
              <div className="space-y-3">
                <div className="flex justify-between">
                  <span className="text-sm text-gray-600">Subtotal</span>
                  <span className="text-sm font-medium">{formatCurrency(order.subtotal, order.currency)}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-sm text-gray-600">Discount</span>
                  <span className="text-sm font-medium text-red-600">
                    -{formatCurrency(order.discount_amount, order.currency)}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-sm text-gray-600">Tax</span>
                  <span className="text-sm font-medium">{formatCurrency(order.tax_amount, order.currency)}</span>
                </div>
                <div className="flex justify-between pt-3 border-t">
                  <span className="font-bold">Total</span>
                  <span className="font-bold text-blue-600">{formatCurrency(order.total_amount, order.currency)}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-sm text-gray-600">Paid</span>
                  <span className="text-sm font-medium text-green-600">{formatCurrency(order.paid_amount, order.currency)}</span>
                </div>
                <div className="flex justify-between pb-3 border-b">
                  <span className="text-sm font-bold text-gray-900">Balance Due</span>
                  <span className="text-sm font-bold text-red-600">
                    {formatCurrency(order.total_amount - order.paid_amount, order.currency)}
                  </span>
                </div>
              </div>
            </div>

            {/* Actions */}
            <div className="bg-white rounded-lg shadow p-6">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">Actions</h2>
              <div className="space-y-2">
                <button
                  onClick={() => window.print()}
                  className="w-full px-4 py-2 bg-blue-50 text-blue-600 rounded-lg hover:bg-blue-100 transition-colors text-sm font-medium"
                >
                  Print / Download PDF
                </button>
                <button
                  onClick={() => alert('Email functionality coming soon')}
                  className="w-full px-4 py-2 bg-purple-50 text-purple-600 rounded-lg hover:bg-purple-100 transition-colors text-sm font-medium"
                >
                  Send Confirmation Email
                </button>
                {order.payment_status !== 'paid' && (
                  <button
                    onClick={() => alert('Payment recording coming soon')}
                    className="w-full px-4 py-2 bg-green-50 text-green-600 rounded-lg hover:bg-green-100 transition-colors text-sm font-medium"
                  >
                    Record Payment
                  </button>
                )}
              </div>
            </div>

            {/* Metadata */}
            <div className="bg-white rounded-lg shadow p-6">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">Metadata</h2>
              <div className="space-y-3 text-sm">
                <div>
                  <p className="text-gray-600">Created</p>
                  <p className="text-gray-900">
                    {new Date(order.created_at).toLocaleString('en-IN')}
                  </p>
                </div>
                <div>
                  <p className="text-gray-600">Last Updated</p>
                  <p className="text-gray-900">
                    {new Date(order.updated_at).toLocaleString('en-IN')}
                  </p>
                </div>
                <div>
                  <p className="text-gray-600">Order ID</p>
                  <p className="text-gray-900 font-mono text-xs break-all">{order.id}</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
