'use client'

/**
 * Loan Restructuring Page
 * List and manage loan restructuring requests
 */

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { restructuringService, type LoanRestructuring } from '@/services/restructuring.service'

export default function RestructuringPage() {
  const router = useRouter()
  const [requests, setRequests] = useState<LoanRestructuring[]>([])
  const [loading, setLoading] = useState(true)
  const [stats, setStats] = useState<any>(null)
  const [filters, setFilters] = useState({
    status: '',
    restructuring_type: '',
    reason: ''
  })

  useEffect(() => {
    loadRequests()
    loadStatistics()
  }, [filters])

  const loadRequests = async () => {
    try {
      setLoading(true)
      const response = await restructuringService.getRequests({
        status: filters.status || undefined,
        restructuring_type: filters.restructuring_type || undefined,
        reason: filters.reason || undefined
      })
      setRequests(response.data.items || [])
    } catch (error) {
      console.error('Failed to load restructuring requests:', error)
    } finally {
      setLoading(false)
    }
  }

  const loadStatistics = async () {
    try {
      const response = await restructuringService.getStatistics()
      setStats(response.data)
    } catch (error) {
      console.error('Failed to load statistics:', error)
    }
  }

  const getStatusColor = (status: string) => {
    const colors: Record<string, string> = {
      pending_approval: 'bg-yellow-100 text-yellow-800',
      approved: 'bg-green-100 text-green-800',
      rejected: 'bg-red-100 text-red-800',
      implemented: 'bg-blue-100 text-blue-800',
      cancelled: 'bg-gray-100 text-gray-800',
      draft: 'bg-gray-100 text-gray-600'
    }
    return colors[status] || 'bg-gray-100 text-gray-800'
  }

  const getTypeLabel = (type: string) => {
    const labels: Record<string, string> = {
      emi_reduction: 'EMI Reduction',
      tenure_extension: 'Tenure Extension',
      moratorium: 'Moratorium',
      interest_rate_reduction: 'Rate Reduction',
      principal_restructure: 'Principal Restructure',
      hybrid: 'Hybrid'
    }
    return labels[type] || type
  }

  const getReasonLabel = (reason: string) => {
    const labels: Record<string, string> = {
      financial_hardship: 'Financial Hardship',
      job_loss: 'Job Loss',
      medical_emergency: 'Medical Emergency',
      business_loss: 'Business Loss',
      natural_disaster: 'Natural Disaster',
      covid_impact: 'COVID Impact',
      other: 'Other'
    }
    return labels[reason] || reason
  }

  return (
    <div className="container mx-auto p-6">
      {/* Header */}
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-gray-900">Loan Restructuring</h1>
        <p className="text-gray-600 mt-2">Manage loan restructuring requests for customer relief</p>
      </div>

      {/* Statistics Cards */}
      {stats && (
        <div className="grid grid-cols-1 md:grid-cols-5 gap-4 mb-6">
          <div className="bg-white p-6 rounded-lg shadow">
            <div className="text-sm text-gray-600">Total Requests</div>
            <div className="text-2xl font-bold text-gray-900">{stats.total_requests}</div>
          </div>
          <div className="bg-white p-6 rounded-lg shadow">
            <div className="text-sm text-gray-600">Pending Approval</div>
            <div className="text-2xl font-bold text-yellow-600">{stats.pending_requests}</div>
          </div>
          <div className="bg-white p-6 rounded-lg shadow">
            <div className="text-sm text-gray-600">Approved</div>
            <div className="text-2xl font-bold text-green-600">{stats.approved_requests}</div>
          </div>
          <div className="bg-white p-6 rounded-lg shadow">
            <div className="text-sm text-gray-600">Implemented</div>
            <div className="text-2xl font-bold text-blue-600">{stats.implemented_requests}</div>
          </div>
          <div className="bg-white p-6 rounded-lg shadow">
            <div className="text-sm text-gray-600">Approval Rate</div>
            <div className="text-2xl font-bold text-purple-600">{stats.approval_rate?.toFixed(1)}%</div>
          </div>
        </div>
      )}

      {/* Actions and Filters */}
      <div className="bg-white p-4 rounded-lg shadow mb-6">
        <div className="flex flex-wrap gap-4 items-center justify-between">
          <div className="flex gap-4">
            <button
              onClick={() => router.push('/loans/restructuring/create')}
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
            >
              + Create Restructuring Request
            </button>
            <button
              onClick={() => router.push('/loans/restructuring/pending')}
              className="px-4 py-2 bg-yellow-600 text-white rounded-lg hover:bg-yellow-700"
            >
              Pending Approvals ({stats?.pending_requests || 0})
            </button>
          </div>

          <div className="flex gap-4">
            <select
              value={filters.status}
              onChange={(e) => setFilters({ ...filters, status: e.target.value })}
              className="px-4 py-2 border border-gray-300 rounded-lg"
            >
              <option value="">All Status</option>
              <option value="pending_approval">Pending Approval</option>
              <option value="approved">Approved</option>
              <option value="rejected">Rejected</option>
              <option value="implemented">Implemented</option>
              <option value="cancelled">Cancelled</option>
            </select>

            <select
              value={filters.restructuring_type}
              onChange={(e) => setFilters({ ...filters, restructuring_type: e.target.value })}
              className="px-4 py-2 border border-gray-300 rounded-lg"
            >
              <option value="">All Types</option>
              <option value="emi_reduction">EMI Reduction</option>
              <option value="tenure_extension">Tenure Extension</option>
              <option value="moratorium">Moratorium</option>
              <option value="interest_rate_reduction">Rate Reduction</option>
            </select>

            <select
              value={filters.reason}
              onChange={(e) => setFilters({ ...filters, reason: e.target.value })}
              className="px-4 py-2 border border-gray-300 rounded-lg"
            >
              <option value="">All Reasons</option>
              <option value="financial_hardship">Financial Hardship</option>
              <option value="job_loss">Job Loss</option>
              <option value="medical_emergency">Medical Emergency</option>
              <option value="covid_impact">COVID Impact</option>
            </select>
          </div>
        </div>
      </div>

      {/* Requests Table */}
      <div className="bg-white rounded-lg shadow overflow-hidden">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Request Number</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Loan Account</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Type</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Reason</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Current EMI</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Proposed EMI</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Created</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Actions</th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {loading ? (
              <tr>
                <td colSpan={9} className="px-6 py-4 text-center text-gray-500">
                  Loading requests...
                </td>
              </tr>
            ) : requests.length === 0 ? (
              <tr>
                <td colSpan={9} className="px-6 py-4 text-center text-gray-500">
                  No restructuring requests found
                </td>
              </tr>
            ) : (
              requests.map((request) => (
                <tr key={request.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm font-medium text-blue-600 cursor-pointer"
                         onClick={() => router.push(`/loans/restructuring/${request.id}`)}>
                      {request.restructuring_number}
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    LA-{request.loan_account_id}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className="text-sm text-gray-900">{getTypeLabel(request.restructuring_type)}</span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className="text-sm text-gray-900">{getReasonLabel(request.reason)}</span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    ₹{request.current_emi.toLocaleString()}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm">
                    {request.proposed_emi ? (
                      <span className={request.proposed_emi < request.current_emi ? 'text-green-600 font-medium' : 'text-gray-900'}>
                        ₹{request.proposed_emi.toLocaleString()}
                      </span>
                    ) : (
                      <span className="text-gray-400">-</span>
                    )}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`px-2 py-1 text-xs rounded ${getStatusColor(request.status)}`}>
                      {request.status.replace('_', ' ')}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {new Date(request.created_at).toLocaleDateString()}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm">
                    <button
                      onClick={() => router.push(`/loans/restructuring/${request.id}`)}
                      className="text-blue-600 hover:text-blue-900 mr-3"
                    >
                      View
                    </button>
                    {request.status === 'pending_approval' && (
                      <button
                        onClick={() => router.push(`/loans/restructuring/${request.id}/approve`)}
                        className="text-green-600 hover:text-green-900"
                      >
                        Review
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
