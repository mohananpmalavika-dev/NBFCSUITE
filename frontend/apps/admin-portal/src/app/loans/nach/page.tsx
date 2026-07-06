'use client'

/**
 * NACH Management Page
 * List and manage NACH mandates
 */

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { nachService, type NACHMandate } from '@/services/nach.service'

export default function NACHPage() {
  const router = useRouter()
  const [mandates, setMandates] = useState<NACHMandate[]>([])
  const [loading, setLoading] = useState(true)
  const [stats, setStats] = useState<any>(null)
  const [filters, setFilters] = useState({
    status: '',
    mandate_type: '',
    search: ''
  })

  useEffect(() => {
    loadMandates()
    loadStatistics()
  }, [filters])

  const loadMandates = async () => {
    try {
      setLoading(true)
      const response = await nachService.getMandates({
        status: filters.status || undefined,
        mandate_type: filters.mandate_type || undefined
      })
      setMandates(response.data.items || [])
    } catch (error) {
      console.error('Failed to load mandates:', error)
    } finally {
      setLoading(false)
    }
  }

  const loadStatistics = async () => {
    try {
      const response = await nachService.getMandateStatistics()
      setStats(response.data)
    } catch (error) {
      console.error('Failed to load statistics:', error)
    }
  }

  const getStatusColor = (status: string) => {
    const colors: Record<string, string> = {
      active: 'bg-green-100 text-green-800',
      pending_bank: 'bg-yellow-100 text-yellow-800',
      pending_customer: 'bg-blue-100 text-blue-800',
      rejected: 'bg-red-100 text-red-800',
      cancelled: 'bg-gray-100 text-gray-800',
      expired: 'bg-orange-100 text-orange-800'
    }
    return colors[status] || 'bg-gray-100 text-gray-800'
  }

  return (
    <div className="container mx-auto p-6">
      {/* Header */}
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-gray-900">NACH Management</h1>
        <p className="text-gray-600 mt-2">Manage NACH/eNACH mandates for automated EMI collection</p>
      </div>

      {/* Statistics Cards */}
      {stats && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
          <div className="bg-white p-6 rounded-lg shadow">
            <div className="text-sm text-gray-600">Total Mandates</div>
            <div className="text-2xl font-bold text-gray-900">{stats.total_mandates}</div>
          </div>
          <div className="bg-white p-6 rounded-lg shadow">
            <div className="text-sm text-gray-600">Active Mandates</div>
            <div className="text-2xl font-bold text-green-600">{stats.active_mandates}</div>
          </div>
          <div className="bg-white p-6 rounded-lg shadow">
            <div className="text-sm text-gray-600">Pending Approval</div>
            <div className="text-2xl font-bold text-yellow-600">{stats.pending_mandates}</div>
          </div>
          <div className="bg-white p-6 rounded-lg shadow">
            <div className="text-sm text-gray-600">Expiring Soon (30d)</div>
            <div className="text-2xl font-bold text-orange-600">{stats.mandates_expiring_30_days}</div>
          </div>
        </div>
      )}

      {/* Actions and Filters */}
      <div className="bg-white p-4 rounded-lg shadow mb-6">
        <div className="flex flex-wrap gap-4 items-center justify-between">
          <div className="flex gap-4">
            <button
              onClick={() => router.push('/loans/nach/create')}
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
            >
              + Create NACH Mandate
            </button>
            <button
              onClick={() => router.push('/loans/nach/debits')}
              className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700"
            >
              View Debit Transactions
            </button>
          </div>

          <div className="flex gap-4">
            <select
              value={filters.status}
              onChange={(e) => setFilters({ ...filters, status: e.target.value })}
              className="px-4 py-2 border border-gray-300 rounded-lg"
            >
              <option value="">All Status</option>
              <option value="active">Active</option>
              <option value="pending_bank">Pending Bank</option>
              <option value="pending_customer">Pending Customer</option>
              <option value="rejected">Rejected</option>
              <option value="cancelled">Cancelled</option>
              <option value="expired">Expired</option>
            </select>

            <select
              value={filters.mandate_type}
              onChange={(e) => setFilters({ ...filters, mandate_type: e.target.value })}
              className="px-4 py-2 border border-gray-300 rounded-lg"
            >
              <option value="">All Types</option>
              <option value="physical">Physical NACH</option>
              <option value="enach">eNACH</option>
            </select>
          </div>
        </div>
      </div>

      {/* Mandates Table */}
      <div className="bg-white rounded-lg shadow overflow-hidden">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Mandate Number</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Type</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Loan Account</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Max Amount</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Frequency</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Valid Until</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Actions</th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {loading ? (
              <tr>
                <td colSpan={8} className="px-6 py-4 text-center text-gray-500">
                  Loading mandates...
                </td>
              </tr>
            ) : mandates.length === 0 ? (
              <tr>
                <td colSpan={8} className="px-6 py-4 text-center text-gray-500">
                  No mandates found
                </td>
              </tr>
            ) : (
              mandates.map((mandate) => (
                <tr key={mandate.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm font-medium text-blue-600 cursor-pointer"
                         onClick={() => router.push(`/loans/nach/${mandate.id}`)}>
                      {mandate.mandate_number}
                    </div>
                    {mandate.umrn && (
                      <div className="text-xs text-gray-500">UMRN: {mandate.umrn}</div>
                    )}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`px-2 py-1 text-xs rounded ${
                      mandate.mandate_type === 'enach' ? 'bg-purple-100 text-purple-800' : 'bg-gray-100 text-gray-800'
                    }`}>
                      {mandate.mandate_type === 'enach' ? 'eNACH' : 'Physical'}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    LA-{mandate.loan_account_id}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    ₹{mandate.max_amount.toLocaleString()}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {mandate.frequency}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`px-2 py-1 text-xs rounded ${getStatusColor(mandate.status)}`}>
                      {mandate.status.replace('_', ' ')}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {new Date(mandate.end_date).toLocaleDateString()}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm">
                    <button
                      onClick={() => router.push(`/loans/nach/${mandate.id}`)}
                      className="text-blue-600 hover:text-blue-900 mr-3"
                    >
                      View
                    </button>
                    {mandate.status === 'pending_bank' && (
                      <button
                        onClick={() => router.push(`/loans/nach/${mandate.id}/approve`)}
                        className="text-green-600 hover:text-green-900"
                      >
                        Approve
                      </button>
                    )}
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  )
}
