'use client'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import { salesApi, Quote } from '@/services/salesApi'

interface QuoteDetailProps {
  quoteId: string
}

export default function QuoteDetail({ quoteId }: QuoteDetailProps) {
  const router = useRouter()
  const [quote, setQuote] = useState<Quote | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    loadQuote()
  }, [quoteId])

  const loadQuote = async () => {
    try {
      setLoading(true)
      setError(null)

      const response = await salesApi.quotes.get(quoteId)

      if (response.success) {
        setQuote(response.data)
      } else {
        setError('Failed to load quote')
      }
    } catch (err: any) {
      setError(err.message || 'Failed to load quote')
    } finally {
      setLoading(false)
    }
  }

  const handleDelete = async () => {
    if (!quote) return

    if (!confirm(`Are you sure you want to delete quote "${quote.quote_number}"?`)) {
      return
    }

    try {
      await salesApi.quotes.delete(quoteId)
      router.push('/crm/quotes')
    } catch (err: any) {
      alert(err.message || 'Failed to delete quote')
    }
  }

  const handleConvertToOrder = async () => {
    if (!quote) return

    if (confirm('Convert this quote to an order?')) {
      router.push(`/crm/orders/new?quote=${quoteId}`)
    }
  }

  const getStatusBadgeColor = (status: string) => {
    switch (status) {
      case 'draft':
        return 'bg-gray-100 text-gray-800'
      case 'sent':
        return 'bg-blue-100 text-blue-800'
      case 'viewed':
        return 'bg-purple-100 text-purple-800'
      case 'accepted':
        return 'bg-green-100 text-green-800'
      case 'rejected':
        return 'bg-red-100 text-red-800'
      case 'expired':
        return 'bg-orange-100 text-orange-800'
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
          <p className="mt-4 text-gray-600">Loading quote...</p>
        </div>
      </div>
    )
  }

  if (error || !quote) {
    return (
      <div className="min-h-screen bg-gray-50 p-6">
        <div className="max-w-4xl mx-auto">
          <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg">
            {error || 'Quote not found'}
          </div>
          <button
            onClick={() => router.push('/crm/quotes')}
            className="mt-4 text-blue-600 hover:text-blue-700"
          >
            ← Back to Quotes
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
            onClick={() => router.push('/crm/quotes')}
            className="text-blue-600 hover:text-blue-700 mb-4 flex items-center"
          >
            ← Back to Quotes
          </button>

          <div className="flex justify-between items-start">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">{quote.quote_number}</h1>
              <p className="text-gray-600 mt-1">Quote Details</p>
            </div>

            <div className="flex gap-2">
              <button
                onClick={() => router.push(`/crm/quotes/${quoteId}/edit`)}
                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
              >
                Edit Quote
              </button>
              {quote.status === 'accepted' && (
                <button
                  onClick={handleConvertToOrder}
                  className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors"
                >
                  Convert to Order
                </button>
              )}
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
            {/* Quote Preview */}
            <div className="bg-white rounded-lg shadow p-8">
              {/* Header */}
              <div className="border-b pb-6 mb-6">
                <div className="flex justify-between items-start">
                  <div>
                    <h2 className="text-2xl font-bold text-gray-900 mb-2">QUOTATION</h2>
                    <p className="text-sm text-gray-600">Quote #: {quote.quote_number}</p>
                  </div>
                  <span className={`text-sm px-3 py-1 rounded-full ${getStatusBadgeColor(quote.status)}`}>
                    {quote.status.toUpperCase()}
                  </span>
                </div>
              </div>

              {/* Bill To */}
              <div className="mb-6">
                <h3 className="text-sm font-semibold text-gray-700 mb-2">BILL TO</h3>
                <p className="text-gray-900 font-medium">{quote.account_name}</p>
              </div>

              {/* Dates */}
              <div className="grid grid-cols-2 gap-4 mb-6">
                <div>
                  <p className="text-sm text-gray-600">Quote Date</p>
                  <p className="text-gray-900 font-medium">{formatDate(quote.quote_date)}</p>
                </div>
                <div>
                  <p className="text-sm text-gray-600">Valid Until</p>
                  <p className="text-gray-900 font-medium">{formatDate(quote.valid_until)}</p>
                </div>
              </div>

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
                    {quote.items?.map((item, index) => (
                      <tr key={index}>
                        <td className="py-3 px-4">
                          <p className="text-sm font-medium text-gray-900">{item.product_name}</p>
                          {item.description && (
                            <p className="text-xs text-gray-600 mt-1">{item.description}</p>
                          )}
                        </td>
                        <td className="text-right py-3 px-4 text-sm text-gray-900">{item.quantity}</td>
                        <td className="text-right py-3 px-4 text-sm text-gray-900">
                          {formatCurrency(item.unit_price, quote.currency)}
                        </td>
                        <td className="text-right py-3 px-4 text-sm text-red-600">
                          {item.discount_amount > 0 ? `-${formatCurrency(item.discount_amount, quote.currency)}` : '-'}
                        </td>
                        <td className="text-right py-3 px-4 text-sm text-gray-900">
                          {formatCurrency(item.tax_amount, quote.currency)}
                        </td>
                        <td className="text-right py-3 px-4 text-sm font-medium text-gray-900">
                          {formatCurrency(item.line_total, quote.currency)}
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
                    <span className="font-medium">{formatCurrency(quote.subtotal, quote.currency)}</span>
                  </div>
                  {quote.discount_amount > 0 && (
                    <div className="flex justify-between text-sm">
                      <span className="text-gray-600">
                        Discount {quote.discount_percentage > 0 ? `(${quote.discount_percentage}%)` : ''}:
                      </span>
                      <span className="font-medium text-red-600">
                        -{formatCurrency(quote.discount_amount, quote.currency)}
                      </span>
                    </div>
                  )}
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-600">Tax:</span>
                    <span className="font-medium">{formatCurrency(quote.tax_amount, quote.currency)}</span>
                  </div>
                  <div className="flex justify-between text-lg font-bold pt-2 border-t">
                    <span>Total:</span>
                    <span className="text-blue-600">{formatCurrency(quote.total_amount, quote.currency)}</span>
                  </div>
                </div>
              </div>

              {/* Terms & Conditions */}
              {quote.terms_conditions && (
                <div className="mt-8 pt-6 border-t">
                  <h3 className="text-sm font-semibold text-gray-700 mb-2">TERMS & CONDITIONS</h3>
                  <p className="text-sm text-gray-600 whitespace-pre-wrap">{quote.terms_conditions}</p>
                </div>
              )}
            </div>

            {/* Internal Notes */}
            {quote.notes && (
              <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-2">Internal Notes</h3>
                <p className="text-sm text-gray-700 whitespace-pre-wrap">{quote.notes}</p>
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
                  <p className="text-sm text-gray-600">Status</p>
                  <span className={`inline-block mt-1 text-sm px-3 py-1 rounded-full ${getStatusBadgeColor(quote.status)}`}>
                    {quote.status.toUpperCase()}
                  </span>
                </div>

                <div>
                  <p className="text-sm text-gray-600">Account</p>
                  <p className="text-sm text-gray-900 mt-1 font-medium">{quote.account_name}</p>
                </div>

                <div>
                  <p className="text-sm text-gray-600">Quote Date</p>
                  <p className="text-sm text-gray-900 mt-1">{formatDate(quote.quote_date)}</p>
                </div>

                <div>
                  <p className="text-sm text-gray-600">Valid Until</p>
                  <p className="text-sm text-gray-900 mt-1">{formatDate(quote.valid_until)}</p>
                </div>

                <div>
                  <p className="text-sm text-gray-600">Currency</p>
                  <p className="text-sm text-gray-900 mt-1">{quote.currency}</p>
                </div>

                <div>
                  <p className="text-sm text-gray-600">Total Items</p>
                  <p className="text-sm text-gray-900 mt-1">{quote.items?.length || 0}</p>
                </div>
              </div>
            </div>

            {/* Summary */}
            <div className="bg-white rounded-lg shadow p-6">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">Summary</h2>
              <div className="space-y-3">
                <div className="flex justify-between">
                  <span className="text-sm text-gray-600">Subtotal</span>
                  <span className="text-sm font-medium">{formatCurrency(quote.subtotal, quote.currency)}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-sm text-gray-600">Discount</span>
                  <span className="text-sm font-medium text-red-600">
                    -{formatCurrency(quote.discount_amount, quote.currency)}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-sm text-gray-600">Tax</span>
                  <span className="text-sm font-medium">{formatCurrency(quote.tax_amount, quote.currency)}</span>
                </div>
                <div className="flex justify-between pt-3 border-t">
                  <span className="text-lg font-bold">Total</span>
                  <span className="text-lg font-bold text-blue-600">
                    {formatCurrency(quote.total_amount, quote.currency)}
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
                  Send via Email
                </button>
                {quote.status === 'accepted' && (
                  <button
                    onClick={handleConvertToOrder}
                    className="w-full px-4 py-2 bg-green-50 text-green-600 rounded-lg hover:bg-green-100 transition-colors text-sm font-medium"
                  >
                    Convert to Order
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
                    {new Date(quote.created_at).toLocaleString('en-IN')}
                  </p>
                </div>
                <div>
                  <p className="text-gray-600">Last Updated</p>
                  <p className="text-gray-900">
                    {new Date(quote.updated_at).toLocaleString('en-IN')}
                  </p>
                </div>
                <div>
                  <p className="text-gray-600">Quote ID</p>
                  <p className="text-gray-900 font-mono text-xs break-all">{quote.id}</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
