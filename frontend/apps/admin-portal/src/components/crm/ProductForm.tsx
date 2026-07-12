'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { salesApi, ProductCreate, ProductUpdate, Product } from '@/services/salesApi'

interface ProductFormProps {
  productId?: string
  mode: 'create' | 'edit'
}

export default function ProductForm({ productId, mode }: ProductFormProps) {
  const router = useRouter()
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [success, setSuccess] = useState<string | null>(null)

  // Form state
  const [formData, setFormData] = useState<ProductCreate>({
    name: '',
    product_code: '',
    description: '',
    category: 'goods',
    status: 'active',
    unit_price: 0,
    cost_price: 0,
    currency: 'INR',
    unit_of_measure: 'unit',
    track_inventory: false,
    stock_quantity: 0,
    reorder_level: 0,
    hsn_sac_code: '',
    tax_rate: 0,
    image_url: '',
    specifications: {},
    tags: [],
  })

  useEffect(() => {
    if (mode === 'edit' && productId) {
      loadProduct()
    }
  }, [productId, mode])

  const loadProduct = async () => {
    if (!productId) return

    try {
      setLoading(true)
      const response = await salesApi.products.get(productId)

      if (response.success) {
        const product = response.data
        setFormData({
          name: product.name,
          product_code: product.product_code,
          description: product.description || '',
          category: product.category,
          status: product.status,
          unit_price: product.unit_price,
          cost_price: product.cost_price || 0,
          currency: product.currency,
          unit_of_measure: product.unit_of_measure,
          track_inventory: product.track_inventory,
          stock_quantity: product.stock_quantity,
          reorder_level: product.reorder_level,
          hsn_sac_code: product.hsn_sac_code || '',
          tax_rate: product.tax_rate || 0,
          image_url: product.image_url || '',
          specifications: product.specifications || {},
          tags: product.tags || [],
        })
      } else {
        setError('Failed to load product')
      }
    } catch (err: any) {
      setError(err.message || 'Failed to load product')
    } finally {
      setLoading(false)
    }
  }

  const handleChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>
  ) => {
    const { name, value, type } = e.target

    if (type === 'checkbox') {
      const checked = (e.target as HTMLInputElement).checked
      setFormData((prev) => ({ ...prev, [name]: checked }))
    } else if (type === 'number') {
      setFormData((prev) => ({ ...prev, [name]: parseFloat(value) || 0 }))
    } else {
      setFormData((prev) => ({ ...prev, [name]: value }))
    }
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setError(null)
    setSuccess(null)

    try {
      if (mode === 'create') {
        const response = await salesApi.products.create(formData)
        if (response.success) {
          setSuccess('Product created successfully!')
          setTimeout(() => {
            router.push(`/crm/products/${response.data.id}`)
          }, 1500)
        } else {
          setError('Failed to create product')
        }
      } else if (mode === 'edit' && productId) {
        const updateData: ProductUpdate = { ...formData }
        const response = await salesApi.products.update(productId, updateData)
        if (response.success) {
          setSuccess('Product updated successfully!')
          setTimeout(() => {
            router.push(`/crm/products/${productId}`)
          }, 1500)
        } else {
          setError('Failed to update product')
        }
      }
    } catch (err: any) {
      setError(err.message || 'Failed to save product')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="mb-6">
          <button
            onClick={() => router.back()}
            className="text-blue-600 hover:text-blue-700 mb-4 flex items-center"
          >
            ← Back
          </button>
          <h1 className="text-3xl font-bold text-gray-900">
            {mode === 'create' ? 'Add New Product' : 'Edit Product'}
          </h1>
          <p className="text-gray-600 mt-1">
            {mode === 'create'
              ? 'Create a new product in your catalog'
              : 'Update product information'}
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

        {/* Form */}
        <form onSubmit={handleSubmit} className="bg-white rounded-lg shadow p-6 space-y-6">
          {/* Basic Information */}
          <div>
            <h2 className="text-xl font-semibold text-gray-900 mb-4">Basic Information</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Product Name <span className="text-red-500">*</span>
                </label>
                <input
                  type="text"
                  name="name"
                  value={formData.name}
                  onChange={handleChange}
                  required
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Product Code <span className="text-red-500">*</span>
                </label>
                <input
                  type="text"
                  name="product_code"
                  value={formData.product_code}
                  onChange={handleChange}
                  required
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="e.g., PROD-001"
                />
              </div>

              <div className="md:col-span-2">
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Description
                </label>
                <textarea
                  name="description"
                  value={formData.description}
                  onChange={handleChange}
                  rows={3}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Category <span className="text-red-500">*</span>
                </label>
                <select
                  name="category"
                  value={formData.category}
                  onChange={handleChange}
                  required
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="goods">Goods</option>
                  <option value="services">Services</option>
                  <option value="software">Software</option>
                  <option value="subscription">Subscription</option>
                  <option value="consulting">Consulting</option>
                  <option value="other">Other</option>
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
                  <option value="active">Active</option>
                  <option value="inactive">Inactive</option>
                  <option value="discontinued">Discontinued</option>
                  <option value="out_of_stock">Out of Stock</option>
                </select>
              </div>
            </div>
          </div>

          {/* Pricing Information */}
          <div>
            <h2 className="text-xl font-semibold text-gray-900 mb-4">Pricing Information</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Unit Price <span className="text-red-500">*</span>
                </label>
                <input
                  type="number"
                  name="unit_price"
                  value={formData.unit_price}
                  onChange={handleChange}
                  required
                  min="0"
                  step="0.01"
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Cost Price
                </label>
                <input
                  type="number"
                  name="cost_price"
                  value={formData.cost_price}
                  onChange={handleChange}
                  min="0"
                  step="0.01"
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
                  Unit of Measure <span className="text-red-500">*</span>
                </label>
                <input
                  type="text"
                  name="unit_of_measure"
                  value={formData.unit_of_measure}
                  onChange={handleChange}
                  required
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="e.g., unit, kg, hour"
                />
              </div>
            </div>
          </div>

          {/* Tax & Compliance */}
          <div>
            <h2 className="text-xl font-semibold text-gray-900 mb-4">Tax & Compliance</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  HSN/SAC Code
                </label>
                <input
                  type="text"
                  name="hsn_sac_code"
                  value={formData.hsn_sac_code}
                  onChange={handleChange}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="e.g., 8517 or 998314"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Tax Rate (%)
                </label>
                <input
                  type="number"
                  name="tax_rate"
                  value={formData.tax_rate}
                  onChange={handleChange}
                  min="0"
                  max="100"
                  step="0.01"
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="e.g., 18.00"
                />
              </div>
            </div>
          </div>

          {/* Inventory Management */}
          <div>
            <h2 className="text-xl font-semibold text-gray-900 mb-4">Inventory Management</h2>
            <div className="space-y-4">
              <div className="flex items-center">
                <input
                  type="checkbox"
                  name="track_inventory"
                  checked={formData.track_inventory}
                  onChange={handleChange}
                  className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                />
                <label className="ml-2 text-sm font-medium text-gray-700">
                  Track Inventory
                </label>
              </div>

              {formData.track_inventory && (
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Stock Quantity
                    </label>
                    <input
                      type="number"
                      name="stock_quantity"
                      value={formData.stock_quantity}
                      onChange={handleChange}
                      min="0"
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Reorder Level
                    </label>
                    <input
                      type="number"
                      name="reorder_level"
                      value={formData.reorder_level}
                      onChange={handleChange}
                      min="0"
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* Additional Information */}
          <div>
            <h2 className="text-xl font-semibold text-gray-900 mb-4">Additional Information</h2>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Image URL
              </label>
              <input
                type="url"
                name="image_url"
                value={formData.image_url}
                onChange={handleChange}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="https://example.com/image.jpg"
              />
            </div>
          </div>

          {/* Form Actions */}
          <div className="flex gap-4 pt-4 border-t">
            <button
              type="submit"
              disabled={loading}
              className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              {loading ? 'Saving...' : mode === 'create' ? 'Create Product' : 'Update Product'}
            </button>
            <button
              type="button"
              onClick={() => router.back()}
              className="px-6 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors"
            >
              Cancel
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}
