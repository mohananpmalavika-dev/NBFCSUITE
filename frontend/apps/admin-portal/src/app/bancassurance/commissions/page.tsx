'use client'

/**
 * Commission Tracking Page
 * Manage agent commissions and payouts
 */

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { 
  DollarSign, TrendingUp, Users, CheckCircle, Clock, XCircle
} from 'lucide-react'
import { bancassuranceService, type InsuranceCommission } from '@/services/bancassurance.service'
import { 
  CommissionType, CommissionStatus,
  COMMISSION_TYPE_LABELS, COMMISSION_STATUS_LABELS, COMMISSION_STATUS_COLORS,
  formatCurrency, formatDate 
} from '@/types/bancassurance'

export default function CommissionsPage() {
  const router = useRouter()
  const [commissions, setCommissions] = useState<InsuranceCommission[]>([])
  const [loading, setLoading] = useState(true)
  const [totalCount, setTotalCount] = useState(0)
  
  // Filters
  const [statusFilter, setStatusFilter] = useState<string>('')
  const [typeFilter, setTypeFilter] = useState<string>('')
  const [page, setPage] = useState(1)
  const [limit] = useState(20)

  useEffect(() => {
    loadCommissions()
  }, [page, statusFilter, typeFilter])

  const loadCommissions = async () => {
    try {
      setLoading(true)
      const response = await bancassuranceService.getCommissions({
        page,
        page_size: limit,
        commission_status: statusFilter || undefined,
        commission_type: typeFilter || undefined,
      })
      
      if (response.data.success) {
        setCommissions(response.data.data.commissions)
        setTotalCount(response.data.data.total)
      }
    } catch (error) {
      console.error('Failed to load commissions:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleApprove = async (id: string) => {
    if (!confirm('Approve this commission for payment?')) return

    try {
      await bancassuranceService.approveCommission(id, {
        approved_by: 'current-user-id', // Would come from auth context
        approval_remarks: 'Approved for payment',
      })
      loadCommissions()
      alert('Commission approved successfully')
    } catch (error) {
      console.error('Failed to approve commission:', error)
      alert('Failed to approve commission')
    }
  }

  const handlePay = async (commission: InsuranceCommission) => {
    const reference = prompt('Enter payment reference number:')
    if (!reference) return

    try {
      await bancassuranceService.payCommission(commission.id, {
        payment_method: 'neft',
        payment_reference: reference,
        paid_amount: commission.net_payable || commission.commission_amount,
      })
      loadCommissions()
      alert('Commission payment recorded successfully')
    } catch (error) {
      console.error('Failed to pay commission:', error)
      alert('Failed to record payment')
    }
  }

  // Calculate totals
  const totalCommissionAmount = commissions.reduce((sum, c) => sum + c.commission_amount, 0)
  const totalPaid = commissions.filter(c => c.commission_status === 'paid').reduce((sum, c) => sum + (c.paid_amount || 0), 0)
  const totalOutstanding = commissions.filter(c => ['pending', 'calculated', 'approved'].includes(c.commission_status)).reduce((sum, c) => sum + c.commission_amount, 0)

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      {/* Header */}
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-gray-900">Commission Tracking</h1>
        <p className="text-gray-600 mt-1">Manage agent commissions and payouts</p>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
        <StatCard 
          title="Total Commissions" 
          value={formatCurrency(totalCommissionAmount)}
          icon={<DollarSign className="w-6 h-6" />}
          color="blue"
        />
        <StatCard 
          title="Paid Amount" 
          value={formatCurrency(totalPaid)}
          icon={<CheckCircle className="w-6 h-6" />}
          color="green"
        />
        <StatCard 
          title="Outstanding" 
          value={formatCurrency(totalOutstanding)}
          icon={<Clock className="w-6 h-6" />}
          color="orange"
        />
        <StatCard 
          title="Total Count" 
          value={totalCount.toString()}
          icon={<TrendingUp className="w-6 h-6" />}
          color="purple"
        />
      </div>

      {/* Filters */}
      <div className="bg-white rounded-lg shadow-sm p-4 mb-6">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Commission Type</label>
            <select
              value={typeFilter}
              onChange={(e) => setTypeFilter(e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
            >
              <option value="">All Types</option>
              {Object.entries(COMMISSION_TYPE_LABELS).map(([value, label]) => (
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
              {Object.entries(COMMISSION_STATUS_LABELS).map(([value, label]) => (
                <option key={value} value={value}>{label}</option>
              ))}
            </select>
          </div>
        </div>
      </div>

      {/* Commissions Table */}
      <div className="bg-white rounded-lg shadow-sm overflow-hidden">
        {loading ? (
          <div className="flex items-center justify-center h-64">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
          </div>
        ) : commissions.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-64 text-gray-500">
            <DollarSign className="w-16 h-16 mb-4 text-gray-400" />
            <p className="text-lg font-medium">No commissions found</p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Commission Details</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Agent</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Policy</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Amount</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
                  <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">Actions</th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {commissions.map((commission) => (
                  <tr key={commission.id} className="hover:bg-gray-50">
                    <td className="px-6 py-4">
                      <div className="flex flex-col">
                        <span className="text-sm font-medium text-gray-900">{commission.commission_number}</span>
                        <span className="text-sm text-gray-500">
                          {COMMISSION_TYPE_LABELS[commission.commission_type as CommissionType]}
                        </span>
                        <span className="text-xs text-gray-400">
                          {formatDate(commission.calculation_date)}
                        </span>
                        {commission.commission_period && (
                          <span className="text-xs text-gray-400">Period: {commission.commission_period}</span>
                        )}
                      </div>
                    </td>
                    <td className="px-6 py-4">
                      <div className="flex flex-col">
                        <span className="text-sm font-medium text-gray-900">{commission.agent_name}</span>
                        {commission.agent_code && (
                          <span className="text-sm text-gray-500">Code: {commission.agent_code}</span>
                        )}
                      </div>
                    </td>
                    <td className="px-6 py-4">
                      <button
                        onClick={() => router.push(`/bancassurance/policies/${commission.policy_id}`)}
                        className="text-sm text-blue-600 hover:underline"
                      >
                        {commission.policy_number}
                      </button>
                    </td>
                    <td className="px-6 py-4">
                      <div className="flex flex-col">
                        <span className="text-sm font-medium text-gray-900">
                          {formatCurrency(commission.commission_amount)}
                        </span>
                        <span className="text-xs text-gray-500">
                          Rate: {commission.commission_rate}%
                        </span>
                        {commission.tds_amount && commission.tds_amount > 0 && (
                          <span className="text-xs text-red-600">
                            TDS: -{formatCurrency(commission.tds_amount)}
                          </span>
                        )}
                        {commission.net_payable && (
                          <span className="text-xs text-green-600 font-medium">
                            Net: {formatCurrency(commission.net_payable)}
                          </span>
                        )}
                      </div>
                    </td>
                    <td className="px-6 py-4">
                      <CommissionStatusBadge status={commission.commission_status as CommissionStatus} />
                      {commission.payment_date && (
                        <div className="text-xs text-gray-500 mt-1">
                          Paid: {formatDate(commission.payment_date)}
                        </div>
                      )}
                    </td>
                    <td className="px-6 py-4 text-right">
                      <div className="flex items-center justify-end gap-2">
                        {commission.commission_status === 'calculated' && (
                          <button
                            onClick={() => handleApprove(commission.id)}
                            className="text-green-600 hover:text-green-900"
                            title="Approve"
                          >
                            <CheckCircle className="w-5 h-5" />
                          </button>
                        )}
                        {commission.commission_status === 'approved' && (
                          <button
                            onClick={() => handlePay(commission)}
                            className="px-3 py-1 text-sm bg-blue-600 text-white rounded hover:bg-blue-700"
                          >
                            Pay
                          </button>
                        )}
                        {commission.commission_status === 'paid' && (
                          <span className="text-sm text-green-600 font-medium">Paid</span>
                        )}
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
            Showing {(page - 1) * limit + 1} to {Math.min(page * limit, totalCount)} of {totalCount} commissions
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

function CommissionStatusBadge({ status }: { status: CommissionStatus }) {
  const color = COMMISSION_STATUS_COLORS[status]
  const label = COMMISSION_STATUS_LABELS[status]
  
  const colorClasses: Record<string, string> = {
    gray: 'bg-gray-100 text-gray-800',
    blue: 'bg-blue-100 text-blue-800',
    green: 'bg-green-100 text-green-800',
    red: 'bg-red-100 text-red-800',
  }

  return (
    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${colorClasses[color]}`}>
      {label}
    </span>
  )
}
