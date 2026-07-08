'use client'

/**
 * Claims Processing Page
 * Manage insurance claims with complete workflow
 */

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { 
  FileText, Search, Plus, CheckCircle, XCircle, Clock, AlertTriangle
} from 'lucide-react'
import { bancassuranceService, type InsuranceClaim } from '@/services/bancassurance.service'
import { 
  ClaimType, ClaimStatus, 
  CLAIM_TYPE_LABELS, CLAIM_STATUS_LABELS, CLAIM_STATUS_COLORS,
  formatCurrency, formatDate 
} from '@/types/bancassurance'

export default function ClaimsPage() {
  const router = useRouter()
  const [claims, setClaims] = useState<InsuranceClaim[]>([])
  const [loading, setLoading] = useState(true)
  const [totalCount, setTotalCount] = useState(0)
  
  // Filters
  const [statusFilter, setStatusFilter] = useState<string>('')
  const [typeFilter, setTypeFilter] = useState<string>('')
  const [page, setPage] = useState(1)
  const [limit] = useState(20)

  useEffect(() => {
    loadClaims()
  }, [page, statusFilter, typeFilter])

  const loadClaims = async () => {
    try {
      setLoading(true)
      const response = await bancassuranceService.getClaims({
        page,
        page_size: limit,
        claim_status: statusFilter || undefined,
        claim_type: typeFilter || undefined,
      })
      
      if (response.data.success) {
        setClaims(response.data.data.claims)
        setTotalCount(response.data.data.total)
      }
    } catch (error) {
      console.error('Failed to load claims:', error)
    } finally {
      setLoading(false)
    }
  }

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'approved': return <CheckCircle className="w-5 h-5 text-green-600" />
      case 'rejected': return <XCircle className="w-5 h-5 text-red-600" />
      case 'settled': return <CheckCircle className="w-5 h-5 text-green-600" />
      case 'under_review': return <Clock className="w-5 h-5 text-yellow-600" />
      default: return <FileText className="w-5 h-5 text-blue-600" />
    }
  }

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      {/* Header */}
      <div className="mb-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Claims Processing</h1>
            <p className="text-gray-600 mt-1">Manage insurance claim workflow</p>
          </div>
          <button
            onClick={() => router.push('/bancassurance/claims/new')}
            className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
          >
            <Plus className="w-5 h-5" />
            Register Claim
          </button>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-5 gap-4 mb-6">
        <StatCard 
          title="Total Claims" 
          value={totalCount.toString()}
          icon={<FileText className="w-6 h-6" />}
          color="blue"
        />
        <StatCard 
          title="Registered" 
          value={claims.filter(c => c.claim_status === 'registered').length.toString()}
          icon={<FileText className="w-6 h-6" />}
          color="gray"
        />
        <StatCard 
          title="Under Review" 
          value={claims.filter(c => c.claim_status === 'under_review').length.toString()}
          icon={<Clock className="w-6 h-6" />}
          color="yellow"
        />
        <StatCard 
          title="Approved" 
          value={claims.filter(c => c.claim_status === 'approved').length.toString()}
          icon={<CheckCircle className="w-6 h-6" />}
          color="green"
        />
        <StatCard 
          title="Settled" 
          value={claims.filter(c => c.claim_status === 'settled').length.toString()}
          icon={<CheckCircle className="w-6 h-6" />}
          color="green"
        />
      </div>

      {/* Filters */}
      <div className="bg-white rounded-lg shadow-sm p-4 mb-6">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Claim Type</label>
            <select
              value={typeFilter}
              onChange={(e) => setTypeFilter(e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
            >
              <option value="">All Types</option>
              {Object.entries(CLAIM_TYPE_LABELS).map(([value, label]) => (
                <option key={value} value={value}>{label}</option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Status</label>
            <select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
            >
              <option value="">All Statuses</option>
              {Object.entries(CLAIM_STATUS_LABELS).map(([value, label]) => (
                <option key={value} value={value}>{label}</option>
              ))}
            </select>
          </div>
        </div>
      </div>

      {/* Claims Table */}
      <div className="bg-white rounded-lg shadow-sm overflow-hidden">
        {loading ? (
          <div className="flex items-center justify-center h-64">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
          </div>
        ) : claims.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-64 text-gray-500">
            <FileText className="w-16 h-16 mb-4 text-gray-400" />
            <p className="text-lg font-medium">No claims found</p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Claim Details</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Policy</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Claimant</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Amount</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
                  <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">Actions</th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {claims.map((claim) => (
                  <tr 
                    key={claim.id} 
                    className="hover:bg-gray-50 cursor-pointer"
                    onClick={() => router.push(`/bancassurance/claims/${claim.id}`)}
                  >
                    <td className="px-6 py-4">
                      <div className="flex items-center gap-3">
                        {getStatusIcon(claim.claim_status)}
                        <div className="flex flex-col">
                          <span className="text-sm font-medium text-gray-900">{claim.claim_number}</span>
                          <span className="text-sm text-gray-500">
                            {CLAIM_TYPE_LABELS[claim.claim_type as ClaimType]}
                          </span>
                          <span className="text-xs text-gray-400">
                            {formatDate(claim.claimed_date)}
                          </span>
                        </div>
                      </div>
                    </td>
                    <td className="px-6 py-4">
                      <button
                        onClick={(e) => {
                          e.stopPropagation()
                          router.push(`/bancassurance/policies/${claim.policy_id}`)
                        }}
                        className="text-sm text-blue-600 hover:underline"
                      >
                        {claim.policy_number}
                      </button>
                    </td>
                    <td className="px-6 py-4">
                      <div className="flex flex-col">
                        <span className="text-sm font-medium text-gray-900">{claim.claimant_name}</span>
                        <span className="text-sm text-gray-500">{claim.claimant_relationship}</span>
                      </div>
                    </td>
                    <td className="px-6 py-4">
                      <div className="flex flex-col">
                        <span className="text-sm font-medium text-gray-900">
                          {formatCurrency(claim.claim_amount)}
                        </span>
                        {claim.assessed_amount && (
                          <span className="text-sm text-blue-600">
                            Assessed: {formatCurrency(claim.assessed_amount)}
                          </span>
                        )}
                        {claim.approved_amount && (
                          <span className="text-sm text-green-600">
                            Approved: {formatCurrency(claim.approved_amount)}
                          </span>
                        )}
                        {claim.settlement_amount && (
                          <span className="text-sm text-green-700 font-medium">
                            Settled: {formatCurrency(claim.settlement_amount)}
                          </span>
                        )}
                      </div>
                    </td>
                    <td className="px-6 py-4">
                      <ClaimStatusBadge status={claim.claim_status as ClaimStatus} />
                      {claim.processing_days && (
                        <div className="text-xs text-gray-500 mt-1">
                          {claim.processing_days} days
                        </div>
                      )}
                    </td>
                    <td className="px-6 py-4 text-right">
                      <button
                        onClick={(e) => {
                          e.stopPropagation()
                          router.push(`/bancassurance/claims/${claim.id}`)
                        }}
                        className="text-blue-600 hover:text-blue-900 text-sm font-medium"
                      >
                        View Details
                      </button>
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
            Showing {(page - 1) * limit + 1} to {Math.min(page * limit, totalCount)} of {totalCount} claims
          </div>
          <div className="flex gap-2">
            <button
              onClick={() => setPage(p => Math.max(1, p - 1))}
              disabled={page === 1}
              className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 disabled:opacity-50"
            >
              Previous
            </button>
            <button
              onClick={() => setPage(p => p + 1)}
              disabled={page * limit >= totalCount}
              className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 disabled:opacity-50"
            >
              Next
            </button>
          </div>
        </div>
      )}
    </div>
  )
}

// Components
function StatCard({ title, value, icon, color }: {
  title: string
  value: string
  icon: React.ReactNode
  color: 'blue' | 'green' | 'yellow' | 'gray'
}) {
  const colorClasses = {
    blue: 'bg-blue-50 text-blue-600',
    green: 'bg-green-50 text-green-600',
    yellow: 'bg-yellow-50 text-yellow-600',
    gray: 'bg-gray-50 text-gray-600',
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

function ClaimStatusBadge({ status }: { status: ClaimStatus }) {
  const color = CLAIM_STATUS_COLORS[status]
  const label = CLAIM_STATUS_LABELS[status]
  
  const colorClasses: Record<string, string> = {
    gray: 'bg-gray-100 text-gray-800',
    blue: 'bg-blue-100 text-blue-800',
    yellow: 'bg-yellow-100 text-yellow-800',
    orange: 'bg-orange-100 text-orange-800',
    purple: 'bg-purple-100 text-purple-800',
    green: 'bg-green-100 text-green-800',
    red: 'bg-red-100 text-red-800',
  }

  return (
    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${colorClasses[color]}`}>
      {label}
    </span>
  )
}
