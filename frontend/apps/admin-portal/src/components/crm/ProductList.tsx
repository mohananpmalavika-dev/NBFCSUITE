'use client'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import { salesApi, Product, ProductListParams } from '@/services/salesApi'

export default function ProductList() {
  const router = useRouter()
  const [products, setProducts] = useState<Product[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [totalPages, setTotalPages] = useState(0)
  const [currentPage, setCurrentPage] = useState(1)
  const [totalRecords, setTotalRecords] = useState(0)
  const pageSize = 20

  // Filters
  const [searchTerm, setSearchTerm] = useState('')
  const [categoryFilter, setCategoryFilter] = useState('')
  const [statusFilter, setStatusFilter] = useState('')

  useEffect(() => {
    loadProducts()
  }, [currentPage, searchTerm, categoryFilter, statusFilter])

  const loadProducts = async () => {
    try {
      setLoading(true)
      setError(null)

      const params: ProductListParams = {
        skip: (currentPage - 1) * pageSize,
        limit: pageSize,
      }

      if (searchTerm) params.search = searchTerm
      if (categoryFilter) params.category = categoryFilter
      if (statusFilter) params.status = statusFilter

      const response = await salesApi.products.list(params)

      if (response.success) {
        setProducts(response.data.products)
        setTotalRecords(response.data.total)
        setTotalPages(response.data.total_pages)
      } else {
        setError('Failed to load products')
      }
    } catch (err: any) {
      setError(err.message || 'Failed to load products')
    } finally {
      setLoading(false)
    }
  }

  const handleSearch = (value: string) => {
    setSearchTerm(value)
    setCurrentPage(1)
  }

  const handleCategoryFilter = (value: string) => {
    setCategoryFilter(value)
    setCurrentPage(1)
  }

  const handleStatusFilter = (value: string) => {
    setStatusFilter(value)
    setCurrentPage(1)
  }

  const handleDelete = async (productId: string, productName: string) => {
    if (!confirm(`Are you sure you want to delete product "${productName}"?`)) {
      return
    }

    try {
      await salesApi.products.delete(productId)
      loadProducts()
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

  const getCategoryBadgeColor = (category: string) => {
    switch (category) {
      case 'goods':
        return 'bg-blue-100 text-blue-800'
      case 'services':
        return 'bg-purple-100 text-purple-800'
      case 'software':
        return 'bg-indigo-100 text-indigo-800'
      case 'subscription':
        return 'bg-pink-100 text-pink-800'
      case 'consulting':
        return 'bg-teal-100 text-teal-800'
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

  if (loading && products.length === 0) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading products...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      {/* Header */}
      <div className="mb-6">
        <div className="flex justify-between items-center mb-4">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Product Catalog</h1>
            <p className="text-gray-600 mt-1">Manage your product and service offerings</p>
          </div>
          <button
            onClick={() => router.push('/crm/products/new')}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          >
            + Add Product
          </button>
        </div>

        {/* Filters */}
        <div className="bg-white rounded-lg shadow p-4">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            {/* Search */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Search
              </label>
              <input
                type="text"
                placeholder="Search products..."
                value={searchTerm}
                onChange={(e) => handleSearch(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>

            {/* Category Filter */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Category
              </label>
              <select
                value={categoryFilter}
                onChange={(e) => handleCategoryFilter(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="">All Categories</option>
                <option value="goods">Goods</option>
                <option value="services">Services</option>
                <option value="software">Software</option>
                <option value="subscription">Subscription</option>
                <option value="consulting">Consulting</option>
                <option value="other">Other</option>
              </select>
            </div>

            {/* Status Filter */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Status
              </label>
              <select
                value={statusFilter}
                onChange={(e) => handleStatusFilter(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="">All Status</option>
                <option value="active">Active</option>
                <option value="inactive">Inactive</option>
                <option value="discontinued">Discontinued</option>
                <option value="out_of_stock">Out of Stock</option>
              </select>
            </div>

            {/* Clear Filters */}
            <div className="flex items-end">
              <button
                onClick={() => {
                  setSearchTerm('')
                  setCategoryFilter('')
                  setStatusFilter('')
                  setCurrentPage(1)
                }}
                className="w-full px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors"
              >
                Clear Filters
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Error Message */}
      {error && (
        <div className="mb-6 bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg">
          {error}
        </div>
      )}

      {/* Products Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
        {products.map((product) => (
          <div
            key={product.id}
            className="bg-white rounded-lg shadow hover:shadow-lg transition-shadow overflow-hidden"
          >
            {/* Product Image */}
            <div className="h-48 bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center">
              {product.image_url ? (
                <img
                  src={product.image_url}
                  alt={product.name}
                  className="w-full h-full object-cover"
                />
              ) : (
                <svg
                  className="w-20 h-20 text-gray-400"
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

            {/* Product Details */}
            <div className="p-4">
              {/* Product Code & Status */}
              <div className="flex justify-between items-start mb-2">
                <span className="text-xs text-gray-500 font-mono">
                  {product.product_code}
                </span>
                <span className={`text-xs px-2 py-1 rounded-full ${getStatusBadgeColor(product.status)}`}>
                  {product.status.replace('_', ' ')}
                </span>
              </div>

              {/* Product Name */}
              <h3 className="text-lg font-semibold text-gray-900 mb-1 line-clamp-2">
                {product.name}
              </h3>

              {/* Category */}
              <span className={`inline-block text-xs px-2 py-1 rounded-full mb-2 ${getCategoryBadgeColor(product.category)}`}>
                {product.category}
              </span>

              {/* Description */}
              {product.description && (
                <p className="text-sm text-gray-600 mb-3 line-clamp-2">
                  {product.description}
                </p>
              )}

              {/* Price */}
              <div className="mb-3">
                <p className="text-2xl font-bold text-gray-900">
                  {formatCurrency(product.unit_price, product.currency)}
                </p>
                <p className="text-xs text-gray-500">
                  per {product.unit_of_measure}
                </p>
              </div>

              {/* Stock Info */}
              {product.track_inventory && (
                <div className="mb-3 text-sm">
                  <span className="text-gray-600">Stock: </span>
                  <span className={product.stock_quantity > product.reorder_level ? 'text-green-600 font-medium' : 'text-orange-600 font-medium'}>
                    {product.stock_quantity} {product.unit_of_measure}
                  </span>
                </div>
              )}

              {/* HSN/SAC Code */}
              {product.hsn_sac_code && (
                <p className="text-xs text-gray-500 mb-3">
                  HSN/SAC: {product.hsn_sac_code}
                </p>
              )}

              {/* Actions */}
              <div className="flex gap-2">
                <button
                  onClick={() => router.push(`/crm/products/${product.id}`)}
                  className="flex-1 px-3 py-2 bg-blue-50 text-blue-600 rounded-lg hover:bg-blue-100 transition-colors text-sm font-medium"
                >
                  View Details
                </button>
                <button
                  onClick={() => router.push(`/crm/products/${product.id}/edit`)}
                  className="px-3 py-2 bg-gray-50 text-gray-600 rounded-lg hover:bg-gray-100 transition-colors text-sm"
                >
                  Edit
                </button>
                <button
                  onClick={() => handleDelete(product.id, product.name)}
                  className="px-3 py-2 bg-red-50 text-red-600 rounded-lg hover:bg-red-100 transition-colors text-sm"
                >
                  Delete
                </button>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Empty State */}
      {!loading && products.length === 0 && (
        <div className="bg-white rounded-lg shadow p-12 text-center">
          <svg
            className="w-16 h-16 text-gray-400 mx-auto mb-4"
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
          <h3 className="text-lg font-medium text-gray-900 mb-2">No products found</h3>
          <p className="text-gray-600 mb-4">
            {searchTerm || categoryFilter || statusFilter
              ? 'Try adjusting your filters'
              : 'Get started by adding your first product'}
          </p>
          <button
            onClick={() => router.push('/crm/products/new')}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          >
            Add Product
          </button>
        </div>
      )}

      {/* Pagination */}
      {totalPages > 1 && (
        <div className="mt-6 bg-white rounded-lg shadow p-4">
          <div className="flex items-center justify-between">
            <p className="text-sm text-gray-600">
              Showing {(currentPage - 1) * pageSize + 1} to{' '}
              {Math.min(currentPage * pageSize, totalRecords)} of {totalRecords} products
            </p>

            <div className="flex gap-2">
              <button
                onClick={() => setCurrentPage(currentPage - 1)}
                disabled={currentPage === 1}
                className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              >
                Previous
              </button>

              <div className="flex gap-1">
                {Array.from({ length: Math.min(5, totalPages) }, (_, i) => {
                  let pageNum
                  if (totalPages <= 5) {
                    pageNum = i + 1
                  } else if (currentPage <= 3) {
                    pageNum = i + 1
                  } else if (currentPage >= totalPages - 2) {
                    pageNum = totalPages - 4 + i
                  } else {
                    pageNum = currentPage - 2 + i
                  }

                  return (
                    <button
                      key={pageNum}
                      onClick={() => setCurrentPage(pageNum)}
                      className={`px-4 py-2 rounded-lg transition-colors ${
                        currentPage === pageNum
                          ? 'bg-blue-600 text-white'
                          : 'border border-gray-300 hover:bg-gray-50'
                      }`}
                    >
                      {pageNum}
                    </button>
                  )
                })}
              </div>

              <button
                onClick={() => setCurrentPage(currentPage + 1)}
                disabled={currentPage === totalPages}
                className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              >
                Next
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
