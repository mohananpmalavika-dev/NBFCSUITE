'use client'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import { crmApi, CRMAccount, AccountListParams } from '@/services/crmApi'

export default function AccountList() {
  const router = useRouter()
  const [accounts, setAccounts] = useState<CRMAccount[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [totalPages, setTotalPages] = useState(0)
  const [currentPage, setCurrentPage] = useState(1)
  const [totalRecords, setTotalRecords] = useState(0)
  const pageSize = 20

  // Filters
  const [searchTerm, setSearchTerm] = useState('')
  const [statusFilter, setStatusFilter] = useState('')
  const [typeFilter, setTypeFilter] = useState('')

  useEffect(() => {
    loadAccounts()
  }, [currentPage, searchTerm, statusFilter, typeFilter])

  const loadAccounts = async () => {
    try {
      setLoading(true)
      setError(null)

      const params: AccountListParams = {
        skip: (currentPage - 1) * pageSize,
        limit: pageSize,
      }

      if (searchTerm) params.search = searchTerm
      if (statusFilter) params.status = statusFilter
      if (typeFilter) params.account_type = typeFilter

      const response = await crmApi.accounts.list(params)

      if (response.success) {
        setAccounts(response.data.accounts)
        setTotalRecords(response.data.total)
        setTotalPages(response.data.total_pages)
      } else {
        setError('Failed to load accounts')
      }
    } catch (err: any) {
      setError(err.message || 'Failed to load accounts')
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

  const handleTypeFilter = (value: string) => {
    setTypeFilter(value)
    setCurrentPage(1)
  }

  const handleDelete = async (accountId: string, accountName: string) => {
    if (!confirm(`Are you sure you want to delete account "${accountName}"?`)) {
      return
    }

    try {
      await crmApi.accounts.delete(accountId)
      loadAccounts()
    } catch (err: any) {
      alert(err.message || 'Failed to delete account')
    }
  }

  if (loading && accounts.length === 0) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading accounts...</p>
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
            <h1 className="text-3xl font-bold text-gray-900">CRM Accounts</h1>
            <p className="text-gray-600 mt-1">Manage your business accounts and relationships</p>
          </div>
          <button
            onClick={() => router.push('/crm/accounts/new')}
            className="px-6 py-3 bg-blue-600 text-white font-semibold rounded-lg hover:bg-blue-700 shadow-md"
          >
            + New Account
          </button>
        </div>

        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
          <div className="bg-white p-4 rounded-lg shadow">
            <p className="text-sm text-gray-600">Total Accounts</p>
            <p className="text-2xl font-bold text-gray-900">{totalRecords}</p>
          </div>
          <div className="bg-white p-4 rounded-lg shadow">
            <p className="text-sm text-gray-600">Active</p>
            <p className="text-2xl font-bold text-green-600">
              {accounts.filter(a => a.status === 'active').length}
            </p>
          </div>
          <div className="bg-white p-4 rounded-lg shadow">
            <p className="text-sm text-gray-600">Prospects</p>
            <p className="text-2xl font-bold text-yellow-600">
              {accounts.filter(a => a.status === 'prospect').length}
            </p>
          </div>
          <div className="bg-white p-4 rounded-lg shadow">
            <p className="text-sm text-gray-600">Customers</p>
            <p className="text-2xl font-bold text-blue-600">
              {accounts.filter(a => a.status === 'customer').length}
            </p>
          </div>
        </div>

        {/* Filters */}
        <div className="bg-white p-4 rounded-lg shadow">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className="md:col-span-2">
              <input
                type="text"
                placeholder="Search accounts by name, number, email, phone..."
                value={searchTerm}
                onChange={(e) => handleSearch(e.target.value)}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>
            <div>
              <select
                value={statusFilter}
                onChange={(e) => handleStatusFilter(e.target.value)}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                <option value="">All Status</option>
                <option value="active">Active</option>
                <option value="inactive">Inactive</option>
                <option value="prospect">Prospect</option>
                <option value="customer">Customer</option>
                <option value="dormant">Dormant</option>
              </select>
            </div>
            <div>
              <select
                value={typeFilter}
                onChange={(e) => handleTypeFilter(e.target.value)}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                <option value="">All Types</option>
                <option value="individual">Individual</option>
                <option value="business">Business</option>
                <option value="partner">Partner</option>
                <option value="vendor">Vendor</option>
              </select>
            </div>
          </div>
        </div>
      </div>

      {/* Error Message */}
      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded mb-4">
          {error}
        </div>
      )}

      {/* Accounts Table */}
      <div className="bg-white rounded-lg shadow overflow-hidden">
        {accounts.length === 0 ? (
          <div className="text-center py-12">
            <p className="text-gray-600 text-lg">No accounts found</p>
            <button
              onClick={() => router.push('/crm/accounts/new')}
              className="mt-4 px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
            >
              Create Your First Account
            </button>
          </div>
        ) : (
          <>
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Account
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Type
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Industry
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Contact
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Status
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Revenue
                    </th>
                    <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Actions
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {accounts.map((account) => (
                    <tr
                      key={account.id}
                      className="hover:bg-gray-50 cursor-pointer"
                      onClick={() => router.push(`/crm/accounts/${account.id}`)}
                    >
                      <td className="px-6 py-4">
                        <div className="flex items-center">
                          <div>
                            <div className="text-sm font-medium text-gray-900">
                              {account.account_name}
                            </div>
                            <div className="text-sm text-gray-500">
                              {account.account_number}
                            </div>
                          </div>
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className="px-2 py-1 inline-flex text-xs leading-5 font-semibold rounded-full bg-blue-100 text-blue-800">
                          {account.account_type}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        {account.industry || '-'}
                      </td>
                      <td className="px-6 py-4">
                        <div className="text-sm text-gray-900">{account.email || '-'}</div>
                        <div className="text-sm text-gray-500">{account.phone || '-'}</div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span
                          className={`px-2 py-1 inline-flex text-xs leading-5 font-semibold rounded-full ${
                            account.status === 'active'
                              ? 'bg-green-100 text-green-800'
                              : account.status === 'prospect'
                              ? 'bg-yellow-100 text-yellow-800'
                              : account.status === 'customer'
                              ? 'bg-blue-100 text-blue-800'
                              : 'bg-gray-100 text-gray-800'
                          }`}
                        >
                          {account.status}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        {account.total_revenue
                          ? `₹${account.total_revenue.toLocaleString()}`
                          : '-'}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                        <button
                          onClick={(e) => {
                            e.stopPropagation()
                            router.push(`/crm/accounts/${account.id}`)
                          }}
                          className="text-blue-600 hover:text-blue-900 mr-3"
                        >
                          View
                        </button>
                        <button
                          onClick={(e) => {
                            e.stopPropagation()
                            router.push(`/crm/accounts/${account.id}/edit`)
                          }}
                          className="text-green-600 hover:text-green-900 mr-3"
                        >
                          Edit
                        </button>
                        <button
                          onClick={(e) => {
                            e.stopPropagation()
                            handleDelete(account.id, account.account_name)
                          }}
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

            {/* Pagination */}
            {totalPages > 1 && (
              <div className="bg-white px-4 py-3 flex items-center justify-between border-t border-gray-200 sm:px-6">
                <div className="flex-1 flex justify-between sm:hidden">
                  <button
                    onClick={() => setCurrentPage(Math.max(1, currentPage - 1))}
                    disabled={currentPage === 1}
                    className="relative inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 disabled:opacity-50"
                  >
                    Previous
                  </button>
                  <button
                    onClick={() => setCurrentPage(Math.min(totalPages, currentPage + 1))}
                    disabled={currentPage === totalPages}
                    className="ml-3 relative inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 disabled:opacity-50"
                  >
                    Next
                  </button>
                </div>
                <div className="hidden sm:flex-1 sm:flex sm:items-center sm:justify-between">
                  <div>
                    <p className="text-sm text-gray-700">
                      Showing{' '}
                      <span className="font-medium">
                        {(currentPage - 1) * pageSize + 1}
                      </span>{' '}
                      to{' '}
                      <span className="font-medium">
                        {Math.min(currentPage * pageSize, totalRecords)}
                      </span>{' '}
                      of <span className="font-medium">{totalRecords}</span> results
                    </p>
                  </div>
                  <div>
                    <nav className="relative z-0 inline-flex rounded-md shadow-sm -space-x-px">
                      <button
                        onClick={() => setCurrentPage(Math.max(1, currentPage - 1))}
                        disabled={currentPage === 1}
                        className="relative inline-flex items-center px-2 py-2 rounded-l-md border border-gray-300 bg-white text-sm font-medium text-gray-500 hover:bg-gray-50 disabled:opacity-50"
                      >
                        Previous
                      </button>
                      {[...Array(totalPages)].map((_, idx) => {
                        const pageNum = idx + 1
                        if (
                          pageNum === 1 ||
                          pageNum === totalPages ||
                          (pageNum >= currentPage - 2 && pageNum <= currentPage + 2)
                        ) {
                          return (
                            <button
                              key={pageNum}
                              onClick={() => setCurrentPage(pageNum)}
                              className={`relative inline-flex items-center px-4 py-2 border text-sm font-medium ${
                                currentPage === pageNum
                                  ? 'z-10 bg-blue-50 border-blue-500 text-blue-600'
                                  : 'bg-white border-gray-300 text-gray-500 hover:bg-gray-50'
                              }`}
                            >
                              {pageNum}
                            </button>
                          )
                        } else if (
                          pageNum === currentPage - 3 ||
                          pageNum === currentPage + 3
                        ) {
                          return (
                            <span
                              key={pageNum}
                              className="relative inline-flex items-center px-4 py-2 border border-gray-300 bg-white text-sm font-medium text-gray-700"
                            >
                              ...
                            </span>
                          )
                        }
                        return null
                      })}
                      <button
                        onClick={() =>
                          setCurrentPage(Math.min(totalPages, currentPage + 1))
                        }
                        disabled={currentPage === totalPages}
                        className="relative inline-flex items-center px-2 py-2 rounded-r-md border border-gray-300 bg-white text-sm font-medium text-gray-500 hover:bg-gray-50 disabled:opacity-50"
                      >
                        Next
                      </button>
                    </nav>
                  </div>
                </div>
              </div>
            )}
          </>
        )}
      </div>
    </div>
  )
}
