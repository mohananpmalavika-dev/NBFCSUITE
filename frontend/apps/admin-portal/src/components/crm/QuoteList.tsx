'use client'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import { salesApi, Quote, QuoteListParams } from '@/services/salesApi'

export default function QuoteList() {
  const router = useRouter()
  const [quotes, setQuotes] = useState<Quote[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [totalPages, setTotalPages] = useState(0)
  const [currentPage, setCurrentPage] = useState(1)
  const [totalRecords, setTotalRecords] = useState(0)
  const pageSize = 20

  // Filters
  const [searchTerm, setSearchTerm] = useState('')
  const [statusFilter, setStatusFilter] = useState('')
  const [accountFilter, setAccountFilter] = useState('')

  useEffect(() => {
    loadQuotes()
  }, [currentPage, searchTerm, statusFilter, accountFilter])

  const loadQuotes = async () => {
    try {
      setLoading(true)
      setError(null)

      const params: QuoteListParams = {
        skip: (currentPage - 1) * pageSize,
        limit: pageSize,
      }

      if (searchTerm) params.search = searchTerm
      if (statusFilter) params.status = statusFilter
      if (accountFilter) params.account_id = accountFilter

      const response = await salesApi.quotes.list(params)

      if (response.success) {
        setQuotes(response.data.quotes)
        setTotalRecords(response.data.total)
        setTotalPages(response.data.total_pages)
      } else {
        setError('Failed to load quotes')
      }
    } catch (err: any) {
      setError(err.message || 'Failed to load quotes')
    } finally {
      setLoading(false)
    }
  }

  const handleSearch = (value: string) => {
    setSearchTerm(value)
    setCurrentPage(1)
  }

  const handleStatusFilter = (value: string) => {
    setStatusFilter(value)
    setCurrentPage(1)
  }

  const handleDelete = async (quoteId: string, quoteNumber: string) => {
    if (!confirm(`Are you sure you want to delete quote "${quoteNumber}"?`)) {
      return
    }

    try {
      await salesApi.quotes.delete(quoteId)
      loadQuotes()
    } catch (err: any) {
      alert(err.message || 'Failed to delete quote')
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
      month: 'short',
      day: 'numeric',
    })
  }

  const isExpiringSoon = (validUntil: string) => {
    const daysUntilExpiry = Math.ceil(
      (new Date(validUntil).getTime() - new Date().getTime()) / (1000 * 60 * 60 * 24)
    )
    return daysUntilExpiry > 0 && daysUntilExpiry <= 7
  }

  if (loading && quotes.length === 0) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading quotes...</p>
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
            <h1 className="text-3xl font-bold text-gray-900">Quote Management</h1>
            <p className="text-gray-600 mt-1">Create and manage sales quotations</p>
          </div>
          <button
            onClick={() => router.push('/crm/quotes/new')}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          >
            + Create Quote
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
                placeholder="Search quotes..."
                value={searchTerm}
                onChange={(e) => handleSearch(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
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
                <option value="draft">Draft</option>
                <option value="sent">Sent</option>
                <option value="viewed">Viewed</option>
                <option value="accepted">Accepted</option>
                <option value="rejected">Rejected</option>
                <option value="expired">Expired</option>
              </select>
            </div>

            {/* Clear Filters */}
            <div className="flex items-end md:col-span-2">
              <button
                onClick={() => {
                  setSearchTerm('')
                  setStatusFilter('')
                  setAccountFilter('')
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

      {/* Quotes Table */}
      <div className="bg-white rounded-lg shadow overflow-hidden">
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Quote Number
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Account
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Date
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Valid Until
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Amount
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Status
                </th>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {quotes.map((quote) => (
                <tr key={quote.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm font-medium text-gray-900">{quote.quote_number}</div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm text-gray-900">{quote.account_name || 'N/A'}</div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm text-gray-900">{formatDate(quote.quote_date)}</div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm text-gray-900">
                      {formatDate(quote.valid_until)}
                      {isExpiringSoon(quote.valid_until) && (
                        <span className="ml-2 text-orange-600 text-xs">⚠️ Expiring soon</span>
                      )}
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm font-medium text-gray-900">
                      {formatCurrency(quote.total_amount, quote.currency)}
                    </div>
                    <div className="text-xs text-gray-500">
                      {quote.items?.length || 0} items
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`inline-block text-xs px-2 py-1 rounded-full ${getStatusBadgeColor(quote.status)}`}>
                      {quote.status.toUpperCase()}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                    <button
                      onClick={() => router.push(`/crm/quotes/${quote.id}`)}
                      className="text-blue-600 hover:text-blue-900 mr-3"
                    >
                      View
                    </button>
                    <button
                      onClick={() => router.push(`/crm/quotes/${quote.id}/edit`)}
                      className="text-gray-600 hover:text-gray-900 mr-3"
                    >
                      Edit
                    </button>
                    <button
                      onClick={() => handleDelete(quote.id, quote.quote_number)}
                      className="text-red-600 hover:text-red-900"
                    >
                      Delete
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Empty State */}
      {!loading && quotes.length === 0 && (
        <div className="bg-white rounded-lg shadow p-12 text-center mt-6">
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
              d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
            />
          </svg>
          <h3 className="text-lg font-medium text-gray-900 mb-2">No quotes found</h3>
          <p className="text-gray-600 mb-4">
            {searchTerm || statusFilter
              ? 'Try adjusting your filters'
              : 'Get started by creating your first quote'}
          </p>
          <button
            onClick={() => router.push('/crm/quotes/new')}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          >
            Create Quote
          </button>
        </div>
      )}

      {/* Pagination */}
      {totalPages > 1 && (
        <div className="mt-6 bg-white rounded-lg shadow p-4">
          <div className="flex items-center justify-between">
            <p className="text-sm text-gray-600">
              Showing {(currentPage - 1) * pageSize + 1} to{' '}
              {Math.min(currentPage * pageSize, totalRecords)} of {totalRecords} quotes
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
