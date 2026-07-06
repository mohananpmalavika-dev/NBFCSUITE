'use client'

/**
 * Loan Insurance Page
 * List and manage loan insurance policies and claims
 */

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { insuranceService, type InsurancePolicy } from '@/services/insurance.service'

export default function InsurancePage() {
  const router = useRouter()
  const [policies, setPolicies] = useState<InsurancePolicy[]>([])
  const [loading, setLoading] = useState(true)
  const [stats, setStats] = useState<any>(null)
  const [activeTab, setActiveTab] = useState<'policies' | 'claims' | 'expiring'>('policies')
  const [filters, setFilters] = useState({
    status: '',
    insurance_type: '',
    is_mandatory: ''
  })

  useEffect(() => {
    loadPolicies()
    loadStatistics()
  }, [filters])

  const loadPolicies = async () => {
    try {
      setLoading(true)
      const response = await insuranceService.getPolicies({
        status: filters.status || undefined,
        insurance_type: filters.insurance_type || undefined,
        is_mandatory: filters.is_mandatory ? filters.is_mandatory === 'true' : undefined
      })
      setPolicies(response.data.items || [])
    } catch (error) {
      console.error('Failed to load policies:', error)
    } finally {
      setLoading(false)
    }
  }

  const loadStatistics = async () {
    try {
      const response = await insuranceService.getStatistics()
      setStats(response.data)
    } catch (error) {
      console.error('Failed to load statistics:', error)
    }
  }

  const getStatusColor = (status: string) => {
    const colors: Record<string, string> = {
      active: 'bg-green-100 text-green-800',
      expired: 'bg-red-100 text-red-800',
      cancelled: 'bg-gray-100 text-gray-800',
      lapsed: 'bg-orange-100 text-orange-800',
      pending_renewal: 'bg-yellow-100 text-yellow-800',
      pending_activation: 'bg-blue-100 text-blue-800'
    }
    return colors[status] || 'bg-gray-100 text-gray-800'
  }

  const getTypeLabel = (type: string) => {
    const labels: Record<string, string> = {
      life: 'Life Insurance',
      credit_protection: 'Credit Protection',
      asset: 'Asset Insurance',
      health: 'Health Insurance',
      property: 'Property Insurance',
      vehicle_comprehensive: 'Vehicle Comprehensive',
      other: 'Other'
    }
    return labels[type] || type
  }

  const getDaysUntilExpiry = (endDate: string) => {
    const today = new Date()
    const expiry = new Date(endDate)
    const diffTime = expiry.getTime() - today.getTime()
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24))
    return diffDays
  }

  return (
    <div className="container mx-auto p-6">
      {/* Header */}
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-gray-900">Loan Insurance</h1>
        <p className="text-gray-600 mt-2">Manage insurance policies and claims for loan protection</p>
      </div>

      {/* Statistics Cards */}
      {stats && (
        <div className="grid grid-cols-1 md:grid-cols-5 gap-4 mb-6">
          <div className="bg-white p-6 rounded-lg shadow">
            <div className="text-sm text-gray-600">Total Policies</div>
            <div className="text-2xl font-bold text-gray-900">{stats.total_policies}</div>
            <div className="text-xs text-gray-500 mt-1">₹{(stats.total_sum_assured / 10000000).toFixed(1)}Cr covered</div>
          </div>
          <div className="bg-white p-6 rounded-lg shadow">
            <div className="text-sm text-gray-600">Active Policies</div>
            <div className="text-2xl font-bold text-green-600">{stats.active_policies}</div>
            <div className="text-xs text-gray-500 mt-1">₹{(stats.total_premium_collected / 100000).toFixed(1)}L premium</div>
          </div>
          <div className="bg-white p-6 rounded-lg shadow">
            <div className="text-sm text-gray-600">Expiring (30d)</div>
            <div className="text-2xl font-bold text-orange-600">{stats.expiring_30_days}</div>
            <div className="text-xs text-gray-500 mt-1">Need renewal</div>
          </div>
          <div className="bg-white p-6 rounded-lg shadow">
            <div className="text-sm text-gray-600">Overdue Premiums</div>
            <div className="text-2xl font-bold text-red-600">{stats.overdue_premium_count}</div>
            <div className="text-xs text-gray-500 mt-1">₹{(stats.total_premiums_overdue / 100000).toFixed(1)}L due</div>
          </div>
          <div className="bg-white p-6 rounded-lg shadow">
            <div className="text-sm text-gray-600">Pending Claims</div>
            <div className="text-2xl font-bold text-yellow-600">{stats.pending_claims}</div>
            <div className="text-xs text-gray-500 mt-1">{stats.claim_settlement_ratio?.toFixed(0)}% settled</div>
          </div>
        </div>
      )}

      {/* Tabs */}
      <div className="mb-6 border-b border-gray-200">
        <nav className="-mb-px flex space-x-8">
          <button
            onClick={() => setActiveTab('policies')}
            className={`py-4 px-1 border-b-2 font-medium text-sm ${
              activeTab === 'policies'
                ? 'border-blue-500 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            }`}
          >
            All Policies
          </button>
          <button
            onClick={() => setActiveTab('expiring')}
            className={`py-4 px-1 border-b-2 font-medium text-sm ${
              activeTab === 'expiring'
                ? 'border-blue-500 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            }`}
          >
            Expiring Soon ({stats?.expiring_30_days || 0})
          </button>
          <button
            onClick={() => setActiveTab('claims')}
            className={`py-4 px-1 border-b-2 font-medium text-sm ${
              activeTab === 'claims'
                ? 'border-blue-500 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            }`}
          >
            Claims ({stats?.pending_claims || 0})
          </button>
        </nav>
      </div>

      {/* Actions and Filters */}
      <div className="bg-white p-4 rounded-lg shadow mb-6">
        <div className="flex flex-wrap gap-4 items-center justify-between">
          <div className="flex gap-4">
            <button
              onClick={() => router.push('/loans/insurance/create')}
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
            >
              + Add Insurance Policy
            </button>
            <button
              onClick={() => router.push('/loans/insurance/claims/create')}
              className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700"
            >
              + File Claim
            </button>
            <button
              onClick={() => router.push('/loans/insurance/dashboard')}
              className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700"
            >
              Dashboard
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
              <option value="expired">Expired</option>
              <option value="cancelled">Cancelled</option>
              <option value="pending_renewal">Pending Renewal</option>
            </select>

            <select
              value={filters.insurance_type}
              onChange={(e) => setFilters({ ...filters, insurance_type: e.target.value })}
              className="px-4 py-2 border border-gray-300 rounded-lg"
            >
              <option value="">All Types</option>
              <option value="life">Life Insurance</option>
              <option value="credit_protection">Credit Protection</option>
              <option value="asset">Asset Insurance</option>
              <option value="vehicle_comprehensive">Vehicle Insurance</option>
            </select>

            <select
              value={filters.is_mandatory}
              onChange={(e) => setFilters({ ...filters, is_mandatory: e.target.value })}
              className="px-4 py-2 border border-gray-300 rounded-lg"
            >
              <option value="">All</option>
              <option value="true">Mandatory Only</option>
              <option value="false">Optional Only</option>
            </select>
          </div>
        </div>
      </div>

      {/* Policies Table */}
      {activeTab === 'policies' && (
        <div className="bg-white rounded-lg shadow overflow-hidden">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Policy Number</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Loan Account</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Type</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Provider</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Sum Assured</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Premium</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Expiry</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Actions</th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {loading ? (
                <tr>
                  <td colSpan={9} className="px-6 py-4 text-center text-gray-500">
                    Loading policies...
                  </td>
                </tr>
              ) : policies.length === 0 ? (
                <tr>
                  <td colSpan={9} className="px-6 py-4 text-center text-gray-500">
                    No insurance policies found
                  </td>
                </tr>
              ) : (
                policies.map((policy) => {
                  const daysToExpiry = getDaysUntilExpiry(policy.policy_end_date)
                  return (
                    <tr key={policy.id} className="hover:bg-gray-50">
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm font-medium text-blue-600 cursor-pointer"
                             onClick={() => router.push(`/loans/insurance/${policy.id}`)}>
                          {policy.policy_number}
                        </div>
                        {policy.is_mandatory && (
                          <span className="text-xs text-red-600">Mandatory</span>
                        )}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        LA-{policy.loan_account_id}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className="text-sm text-gray-900">{getTypeLabel(policy.insurance_type)}</span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        {policy.insurance_provider}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        ₹{policy.sum_assured.toLocaleString()}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        ₹{policy.premium_amount.toLocaleString()}
                        <div className="text-xs text-gray-500">{policy.premium_frequency}</div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className={`px-2 py-1 text-xs rounded ${getStatusColor(policy.status)}`}>
                          {policy.status.replace('_', ' ')}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm text-gray-900">
                          {new Date(policy.policy_end_date).toLocaleDateString()}
                        </div>
                        {daysToExpiry > 0 && daysToExpiry <= 30 && (
                          <div className="text-xs text-orange-600">
                            {daysToExpiry} days left
                          </div>
                        )}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm">
                        <button
                          onClick={() => router.push(`/loans/insurance/${policy.id}`)}
                          className="text-blue-600 hover:text-blue-900 mr-3"
                        >
                          View
                        </button>
                        {policy.status === 'active' && daysToExpiry <= 60 && (
                          <button
                            onClick={() => router.push(`/loans/insurance/${policy.id}/renew`)}
                            className="text-green-600 hover:text-green-900"
                          >
                            Renew
                          </button>
                        )}
                      </td>
                    </tr>
                  )
                })
              )}
            </tbody>
          </table>
        </div>
      )}

      {/* Expiring Policies */}
      {activeTab === 'expiring' && (
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Policies Expiring Soon</h3>
          <p className="text-gray-600">Loading expiring policies...</p>
        </div>
      )}

      {/* Claims */}
      {activeTab === 'claims' && (
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Insurance Claims</h3>
          <p className="text-gray-600">Loading claims...</p>
        </div>
      )}
    </div>
  )
}
