'use client'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import { salesApi, Product } from '@/services/salesApi'

interface ProductDetailProps {
  productId: string
}

export default function ProductDetail({ productId }: ProductDetailProps) {
  const router = useRouter()
  const [product, setProduct] = useState<Product | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    loadProduct()
  }, [productId])

  const loadProduct = async () => {
    try {
      setLoading(true)
      setError(null)

      const response = await salesApi.products.get(productId)

      if (response.success) {
        setProduct(response.data)
      } else {
        setError('Failed to load product')
      }
    } catch (err: any) {
      setError(err.message || 'Failed to load product')
    } finally {
      setLoading(false)
    }
  }

  const handleDelete = async () => {
    if (!product) return

    if (!confirm(`Are you sure you want to delete product "${product.name}"?`)) {
      return
    }

    try {
      await salesApi.products.delete(productId)
      router.push('/crm/products')
    } catch (err: any) {
      alert(err.message || 'Failed to delete product')
    }
  }

  const getStatusBadgeColor = (status: string) => {
    switch (status) {
      case 'active':
        return 'bg-green-100 text-green-800'
      case 'inactive':
        return 'bg-gray-100 text-gray-800'
      case 'discontinued':
        return 'bg-red-100 text-red-800'
      case 'out_of_stock':
        return 'bg-yellow-100 text-yellow-800'
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
      hour: '2-digit',
      minute: '2-digit',
    })
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading product...</p>
        </div>
      </div>
    )
  }

  if (error || !product) {
    return (
      <div className="min-h-screen bg-gray-50 p-6">
        <div className="max-w-4xl mx-auto">
          <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg">
            {error || 'Product not found'}
          </div>
          <button
            onClick={() => router.push('/crm/products')}
            className="mt-4 text-blue-600 hover:text-blue-700"
          >
            ← Back to Products
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
            onClick={() => router.push('/crm/products')}
            className="text-blue-600 hover:text-blue-700 mb-4 flex items-center"
          >
            ← Back to Products
          </button>

          <div className="flex justify-between items-start">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">{product.name}</h1>
              <p className="text-gray-600 mt-1">Product Code: {product.product_code}</p>
            </div>

            <div className="flex gap-2">
              <button
                onClick={() => router.push(`/crm/products/${productId}/edit`)}
                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
              >
                Edit Product
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
            {/* Product Image */}
            <div className="bg-white rounded-lg shadow p-6">
              <div className="h-96 bg-gradient-to-br from-blue-50 to-indigo-100 rounded-lg flex items-center justify-center overflow-hidden">
                {product.image_url ? (
                  <img
                    src={product.image_url}
                    alt={product.name}
                    className="w-full h-full object-contain"
                  />
                ) : (
                  <svg
                    className="w-32 h-32 text-gray-400"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4"
                    />
                  </svg>
                )}
              </div>
            </div>

            {/* Description */}
            <div className="bg-white rounded-lg shadow p-6">
              <h2 className="text-xl font-semibold text-gray-900 mb-4">Description</h2>
              {product.description ? (
                <p className="text-gray-700 whitespace-pre-wrap">{product.description}</p>
              ) : (
                <p className="text-gray-500 italic">No description available</p>
              )}
            </div>

            {/* Pricing Details */}
            <div className="bg-white rounded-lg shadow p-6">
              <h2 className="text-xl font-semibold text-gray-900 mb-4">Pricing Details</h2>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <p className="text-sm text-gray-600">Unit Price</p>
                  <p className="text-2xl font-bold text-gray-900">
                    {formatCurrency(product.unit_price, product.currency)}
                  </p>
                  <p className="text-sm text-gray-500">per {product.unit_of_measure}</p>
                </div>

                {product.cost_price > 0 && (
                  <div>
                    <p className="text-sm text-gray-600">Cost Price</p>
                    <p className="text-2xl font-bold text-gray-900">
                      {formatCurrency(product.cost_price, product.currency)}
                    </p>
                    <p className="text-sm text-gray-500">per {product.unit_of_measure}</p>
                  </div>
                )}

                {product.cost_price > 0 && (
                  <div>
                    <p className="text-sm text-gray-600">Profit Margin</p>
                    <p className="text-2xl font-bold text-green-600">
                      {(((product.unit_price - product.cost_price) / product.cost_price) * 100).toFixed(2)}%
                    </p>
                  </div>
                )}

                {product.tax_rate > 0 && (
                  <div>
                    <p className="text-sm text-gray-600">Tax Rate</p>
                    <p className="text-2xl font-bold text-gray-900">{product.tax_rate}%</p>
                  </div>
                )}
              </div>
            </div>

            {/* Inventory Details */}
            {product.track_inventory && (
              <div className="bg-white rounded-lg shadow p-6">
                <h2 className="text-xl font-semibold text-gray-900 mb-4">Inventory</h2>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <p className="text-sm text-gray-600">Current Stock</p>
                    <p className={`text-2xl font-bold ${product.stock_quantity > product.reorder_level ? 'text-green-600' : 'text-orange-600'}`}>
                      {product.stock_quantity} {product.unit_of_measure}
                    </p>
                  </div>

                  <div>
                    <p className="text-sm text-gray-600">Reorder Level</p>
                    <p className="text-2xl font-bold text-gray-900">
                      {product.reorder_level} {product.unit_of_measure}
                    </p>
                  </div>

                  {product.stock_quantity <= product.reorder_level && (
                    <div className="col-span-2">
                      <div className="bg-orange-50 border border-orange-200 text-orange-700 px-4 py-3 rounded-lg">
                        ⚠️ Stock is at or below reorder level. Consider restocking.
                      </div>
                    </div>
                  )}
                </div>
              </div>
            )}

            {/* Specifications */}
            {product.specifications && Object.keys(product.specifications).length > 0 && (
              <div className="bg-white rounded-lg shadow p-6">
                <h2 className="text-xl font-semibold text-gray-900 mb-4">Specifications</h2>
                <dl className="grid grid-cols-2 gap-4">
                  {Object.entries(product.specifications).map(([key, value]) => (
                    <div key={key}>
                      <dt className="text-sm font-medium text-gray-600">{key}</dt>
                      <dd className="text-sm text-gray-900 mt-1">{String(value)}</dd>
                    </div>
                  ))}
                </dl>
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
                  <span className={`inline-block mt-1 text-sm px-3 py-1 rounded-full ${getStatusBadgeColor(product.status)}`}>
                    {product.status.replace('_', ' ').toUpperCase()}
                  </span>
                </div>

                <div>
                  <p className="text-sm text-gray-600">Category</p>
                  <p className="text-sm text-gray-900 mt-1 capitalize">{product.category}</p>
                </div>

                <div>
                  <p className="text-sm text-gray-600">Currency</p>
                  <p className="text-sm text-gray-900 mt-1">{product.currency}</p>
                </div>

                <div>
                  <p className="text-sm text-gray-600">Unit of Measure</p>
                  <p className="text-sm text-gray-900 mt-1">{product.unit_of_measure}</p>
                </div>

                {product.hsn_sac_code && (
                  <div>
                    <p className="text-sm text-gray-600">HSN/SAC Code</p>
                    <p className="text-sm text-gray-900 mt-1 font-mono">{product.hsn_sac_code}</p>
                  </div>
                )}

                <div>
                  <p className="text-sm text-gray-600">Inventory Tracking</p>
                  <p className="text-sm text-gray-900 mt-1">
                    {product.track_inventory ? 'Enabled' : 'Disabled'}
                  </p>
                </div>
              </div>
            </div>

            {/* Tags */}
            {product.tags && product.tags.length > 0 && (
              <div className="bg-white rounded-lg shadow p-6">
                <h2 className="text-lg font-semibold text-gray-900 mb-4">Tags</h2>
                <div className="flex flex-wrap gap-2">
                  {product.tags.map((tag, index) => (
                    <span
                      key={index}
                      className="px-3 py-1 bg-blue-100 text-blue-800 text-sm rounded-full"
                    >
                      {tag}
                    </span>
                  ))}
                </div>
              </div>
            )}

            {/* Metadata */}
            <div className="bg-white rounded-lg shadow p-6">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">Metadata</h2>
              <div className="space-y-3 text-sm">
                <div>
                  <p className="text-gray-600">Created</p>
                  <p className="text-gray-900">{formatDate(product.created_at)}</p>
                </div>
                <div>
                  <p className="text-gray-600">Last Updated</p>
                  <p className="text-gray-900">{formatDate(product.updated_at)}</p>
                </div>
                <div>
                  <p className="text-gray-600">Product ID</p>
                  <p className="text-gray-900 font-mono text-xs">{product.id}</p>
                </div>
              </div>
            </div>

            {/* Actions */}
            <div className="bg-white rounded-lg shadow p-6">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">Actions</h2>
              <div className="space-y-2">
                <button
                  onClick={() => router.push(`/crm/quotes/new?product=${productId}`)}
                  className="w-full px-4 py-2 bg-blue-50 text-blue-600 rounded-lg hover:bg-blue-100 transition-colors text-sm font-medium"
                >
                  Create Quote
                </button>
                <button
                  onClick={() => router.push(`/crm/orders/new?product=${productId}`)}
                  className="w-full px-4 py-2 bg-green-50 text-green-600 rounded-lg hover:bg-green-100 transition-colors text-sm font-medium"
                >
                  Create Order
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
