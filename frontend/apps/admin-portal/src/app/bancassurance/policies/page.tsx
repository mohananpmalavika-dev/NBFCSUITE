'use client'

/**
 * Insurance Policies Management Page
 * Lists all insurance policies with filtering and actions
 */

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { 
  Plus, Search, Filter, FileText, MoreVertical, 
  CheckCircle, XCircle, RefreshCw, TrendingUp, AlertTriangle 
} from 'lucide-react'
import { bancassuranceService, type InsurancePolicy } from '@/services/bancassurance.service'
import { 
  PolicyType, PolicyStatus, 
  POLICY_TYPE_LABELS, POLICY_STATUS_LABELS, POLICY_STATUS_COLORS,
  formatCurrency, formatDate 
} from '@/types/bancassurance'

export default function PoliciesPage() {
  const router = useRouter()
  const [policies, setPolicies] = useState<InsurancePolicy[]>([])
  const [loading, setLoading] = useState(true)
  const [totalCount, setTotalCount] = useState(0)
  
  // Filters
  const [searchTerm, setSearchTerm] = useState('')
  const [policyType, setPolicyType] = useState<string>('')
  const [policyStatus, setPolicyStatus] = useState<string>('')
  const [page, setPage] = useState(1)
  const [limit] = useState(20)

  // Load policies
  useEffect(() => {
    loadPolicies()
  }, [page, policyType, policyStatus])

  const loadPolicies = async () => {
    try {
      setLoading(true)
      const response = await bancassuranceService.getPolicies({
        page,
        page_size: limit,
        policy_type: policyType || undefined,
        policy_status: policyStatus || undefined,
      })
      
      if (response.data.success) {
        setPolicies(response.data.data.policies)
        setTotalCount(response.data.data.total)
      }
    } catch (error) {
      console.error('Failed to load policies:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleSearch = () => {
    setPage(1)
    loadPolicies()
  }

  const handleActivate = async (id: string) => {
    if (confirm('Activate this policy? This will generate the premium schedule.')) {
      try {
        await bancassuranceService.activatePolicy(id)
        loadPolicies()
      } catch (error) {
        console.error('Failed to activate policy:', error)
        alert('Failed to activate policy')
      }
    }
  }

  const handleLapse = async (id: string) => {
    const reason = prompt('Enter lapse reason:')
    if (reason) {
      try {
        await bancassuranceService.lapsePolicy(id, reason)
        loadPolicies()
      } catch (error) {
        console.error('Failed to lapse policy:', error)
        alert('Failed to lapse policy')
      }
    }
  }

  // Filter UI
  const filteredPolicies = policies.filter(policy => {
    if (!searchTerm) return true
    const search = searchTerm.toLowerCase()
    return (
      policy.policy_number.toLowerCase().includes(search) ||
      policy.customer_name.toLowerCase().includes(search) ||
      policy.insured_name.toLowerCase().includes(search) ||
      policy.insurance_company.toLowerCase().includes(search)
    )
  })

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      {/* Header */}
      <div className="mb-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Insurance Policies</h1>
            <p className="text-gray-600 mt-1">Manage insurance and bancassurance policies</p>
          </div>
          <button
            onClick={() => router.push('/bancassurance/policies/new')}
            className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          >
            <Plus className="w-5 h-5" />
            New Policy
          </button>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
        <StatCard 
          title="Total Policies" 
          value={totalCount.toString()}
          icon={<FileText className="w-6 h-6" />}
          color="blue"
        />
        <StatCard 
          title="Active Policies" 
          value={policies.filter(p => p.policy_status === 'active').length.toString()}
          icon={<CheckCircle className="w-6 h-6" />}
          color="green"
        />
        <StatCard 
          title="Lapsed Policies" 
          value={policies.filter(p => p.is_lapsed).length.toString()}
          icon={<AlertTriangle className="w-6 h-6" />}
          color="orange"
        />
        <StatCard 
          title="Total Sum Assured" 
          value={formatCurrency(policies.reduce((sum, p) => sum + p.sum_assured, 0))}
          icon={<TrendingUp className="w-6 h-6" />}
          color="purple"
        />
      </div>

      {/* Filters */}
      <div className="bg-white rounded-lg shadow-sm p-4 mb-6">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          {/* Search */}
          <div className="md:col-span-2">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
              <input
                type="text"
                placeholder="Search by policy number, customer, or company..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
                className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>
          </div>

          {/* Policy Type Filter */}
          <div>
            <select
              value={policyType}
              onChange={(e) => setPolicyType(e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="">All Types</option>
              {Object.entries(POLICY_TYPE_LABELS).map(([value, label]) => (
                <option key={value} value={value}>{label}</option>
              ))}
            </select>
          </div>

          {/* Status Filter */}
          <div>
            <select
              value={policyStatus}
              onChange={(e) => setPolicyStatus(e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="">All Statuses</option>
              {Object.entries(POLICY_STATUS_LABELS).map(([value, label]) => (
                <option key={value} value={value}>{label}</option>
              ))}
            </select>
          </div>
        </div>
      </div>

      {/* Policies Table */}
      <div className="bg-white rounded-lg shadow-sm overflow-hidden">
        {loading ? (
          <div className="flex items-center justify-center h-64">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
          </div>
        ) : filteredPolicies.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-64 text-gray-500">
            <FileText className="w-16 h-16 mb-4 text-gray-400" />
            <p className="text-lg font-medium">No policies found</p>
            <p className="text-sm">Create a new policy to get started</p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Policy Details
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Customer
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Coverage
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Premium
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
                {filteredPolicies.map((policy) => (
                  <tr 
                    key={policy.id} 
                    className="hover:bg-gray-50 cursor-pointer"
                    onClick={() => router.push(`/bancassurance/policies/${policy.id}`)}
                  >
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex flex-col">
                        <span className="text-sm font-medium text-gray-900">
                          {policy.policy_number}
                        </span>
                        <span className="text-sm text-gray-500">
                          {POLICY_TYPE_LABELS[policy.policy_type as PolicyType]}
                        </span>
                        <span className="text-xs text-gray-400">
                          {policy.insurance_company}
                        </span>
                      </div>
                    </td>
                    <td className="px-6 py-4">
                      <div className="flex flex-col">
                        <span className="text-sm font-medium text-gray-900">
                          {policy.customer_name}
                        </span>
                        <span className="text-sm text-gray-500">
                          Insured: {policy.insured_name}
                        </span>
                        <span className="text-xs text-gray-400">
                          Age: {policy.insured_age} years
                        </span>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex flex-col">
                        <span className="text-sm font-medium text-gray-900">
                          {formatCurrency(policy.sum_assured)}
                        </span>
                        <span className="text-sm text-gray-500">
                          {policy.policy_term_years} years
                        </span>
                        <span className="text-xs text-gray-400">
                          {formatDate(policy.policy_start_date)} - {formatDate(policy.policy_end_date)}
                        </span>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex flex-col">
                        <span className="text-sm font-medium text-gray-900">
                          {formatCurrency(policy.premium_amount)}
                        </span>
                        <span className="text-sm text-gray-500 capitalize">
                          {policy.premium_frequency.replace('_', ' ')}
                        </span>
                        <span className="text-xs text-gray-400">
                          Paid: {formatCurrency(policy.total_premium_paid)}
                        </span>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <StatusBadge 
                        status={policy.policy_status as PolicyStatus}
                        isLapsed={policy.is_lapsed}
                      />
                      {policy.next_premium_due_date && (
                        <div className="text-xs text-gray-500 mt-1">
                          Next: {formatDate(policy.next_premium_due_date)}
                        </div>
                      )}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                      <div className="flex items-center justify-end gap-2">
                        {policy.policy_status === 'draft' && (
                          <button
                            onClick={(e) => {
                              e.stopPropagation()
                              handleActivate(policy.id)
                            }}
                            className="text-green-600 hover:text-green-900"
                            title="Activate Policy"
                          >
                            <CheckCircle className="w-5 h-5" />
                          </button>
                        )}
                        {policy.policy_status === 'active' && (
                          <button
                            onClick={(e) => {
                              e.stopPropagation()
                              handleLapse(policy.id)
                            }}
                            className="text-orange-600 hover:text-orange-900"
                            title="Mark as Lapsed"
                          >
                            <AlertTriangle className="w-5 h-5" />
                          </button>
                        )}
                        <button
                          onClick={(e) => {
                            e.stopPropagation()
                            router.push(`/bancassurance/policies/${policy.id}`)
                          }}
                          className="text-blue-600 hover:text-blue-900"
                        >
                          <MoreVertical className="w-5 h-5" />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Pagination */}
      {totalCount > limit && (
        <div className="mt-6 flex items-center justify-between">
          <div className="text-sm text-gray-700">
            Showing {(page - 1) * limit + 1} to {Math.min(page * limit, totalCount)} of {totalCount} policies
          </div>
          <div className="flex gap-2">
            <button
              onClick={() => setPage(p => Math.max(1, p - 1))}
              disabled={page === 1}
              className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Previous
            </button>
            <button
              onClick={() => setPage(p => p + 1)}
              disabled={page * limit >= totalCount}
              className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Next
            </button>
          </div>
        </div>
      )}
    </div>
  )
}

// Stat Card Component
function StatCard({ title, value, icon, color }: {
  title: string
  value: string
  icon: React.ReactNode
  color: 'blue' | 'green' | 'orange' | 'purple'
}) {
  const colorClasses = {
    blue: 'bg-blue-50 text-blue-600',
    green: 'bg-green-50 text-green-600',
    orange: 'bg-orange-50 text-orange-600',
    purple: 'bg-purple-50 text-purple-600',
  }

  return (
    <div className="bg-white rounded-lg shadow-sm p-6">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm font-medium text-gray-600">{title}</p>
          <p className="text-2xl font-bold text-gray-900 mt-2">{value}</p>
        </div>
        <div className={`p-3 rounded-lg ${colorClasses[color]}`}>
          {icon}
        </div>
      </div>
    </div>
  )
}

// Status Badge Component
function StatusBadge({ status, isLapsed }: { status: PolicyStatus; isLapsed: boolean }) {
  const color = POLICY_STATUS_COLORS[status]
  const label = POLICY_STATUS_LABELS[status]
  
  const colorClasses = {
    gray: 'bg-gray-100 text-gray-800',
    green: 'bg-green-100 text-green-800',
    orange: 'bg-orange-100 text-orange-800',
    red: 'bg-red-100 text-red-800',
    blue: 'bg-blue-100 text-blue-800',
    purple: 'bg-purple-100 text-purple-800',
    yellow: 'bg-yellow-100 text-yellow-800',
  }

  return (
    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${colorClasses[color as keyof typeof colorClasses]}`}>
      {isLapsed ? 'Lapsed' : label}
    </span>
  )
}
