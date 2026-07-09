/**
 * Premium Collection Page
 * Manage premium payments and tracking
 */

'use client'

import { Suspense, useState, useEffect } from 'react'
import { useRouter, useSearchParams } from 'next/navigation'
import { DollarSign, Clock, AlertCircle, CheckCircle, XCircle } from 'lucide-react'
import { bancassuranceService, type InsurancePremium } from '@/services/bancassurance.service'
import {
  PREMIUM_STATUS_LABELS,
  PREMIUM_STATUS_COLORS,
  formatCurrency,
  formatDate,
  getDaysRemaining,
  isOverdue,
  type PremiumStatus
} from '@/types/bancassurance'

function PremiumsContent() {
  const router = useRouter()
  const searchParams = useSearchParams()
  const policyIdFilter = searchParams.get('policy_id')
  
  const [premiums, setPremiums] = useState<InsurancePremium[]>([])
  const [loading, setLoading] = useState(true)
  const [totalCount, setTotalCount] = useState(0)
  const [selectedPremium, setSelectedPremium] = useState<InsurancePremium | null>(null)
  const [showPaymentModal, setShowPaymentModal] = useState(false)
  
  // Filters
  const [statusFilter, setStatusFilter] = useState<string>('')
  const [page, setPage] = useState(1)
  const [limit] = useState(20)

  useEffect(() => {
    loadPremiums()
  }, [page, statusFilter, policyIdFilter])

  const loadPremiums = async () => {
    try {
      setLoading(true)
      const response = await bancassuranceService.getPremiums({
        page,
        page_size: limit,
        premium_status: statusFilter || undefined,
        policy_id: policyIdFilter || undefined,
      })
      
      if (response.data.success) {
        setPremiums(response.data.data.premiums)
        setTotalCount(response.data.data.total)
      }
    } catch (error) {
      console.error('Failed to load premiums:', error)
    } finally {
      setLoading(false)
    }
  }

  const handlePayment = (premium: InsurancePremium) => {
    setSelectedPremium(premium)
    setShowPaymentModal(true)
  }

  const handleWaive = async (premium: InsurancePremium) => {
    const reason = prompt('Enter waiver reason:')
    if (!reason) return

    try {
      await bancassuranceService.waivePremium(premium.id, {
        waived_amount: premium.premium_amount,
        waived_reason: reason,
      })
      loadPremiums()
      alert('Premium waived successfully')
    } catch (error) {
      console.error('Failed to waive premium:', error)
      alert('Failed to waive premium')
    }
  }

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      {/* Header */}
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-gray-900">Premium Collection</h1>
        <p className="text-gray-600 mt-1">Track and collect insurance premiums</p>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
        <StatCard 
          title="Total Premiums" 
          value={totalCount.toString()}
          icon={<DollarSign className="w-6 h-6" />}
          color="blue"
        />
        <StatCard 
          title="Due Premiums" 
          value={premiums.filter(p => p.premium_status === 'due').length.toString()}
          icon={<Clock className="w-6 h-6" />}
          color="yellow"
        />
        <StatCard 
          title="Overdue" 
          value={premiums.filter(p => p.premium_status === 'overdue').length.toString()}
          icon={<AlertCircle className="w-6 h-6" />}
          color="red"
        />
        <StatCard 
          title="Paid" 
          value={premiums.filter(p => p.premium_status === 'paid').length.toString()}
          icon={<CheckCircle className="w-6 h-6" />}
          color="green"
        />
      </div>

      {/* Filters */}
      <div className="bg-white rounded-lg shadow-sm p-4 mb-6">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Status</label>
            <select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
            >
              <option value="">All Statuses</option>
              {Object.entries(PREMIUM_STATUS_LABELS).map(([value, label]) => (
                <option key={value} value={value}>{label}</option>
              ))}
            </select>
          </div>
          
          <div className="flex items-end">
            <button
              onClick={() => router.push('/bancassurance/premiums/overdue')}
              className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700"
            >
              View Overdue Premiums
            </button>
          </div>
        </div>
      </div>

      {/* Premiums Table */}
      <div className="bg-white rounded-lg shadow-sm overflow-hidden">
        {loading ? (
          <div className="flex items-center justify-center h-64">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
          </div>
        ) : premiums.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-64 text-gray-500">
            <DollarSign className="w-16 h-16 mb-4 text-gray-400" />
            <p className="text-lg font-medium">No premiums found</p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Premium Details</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Policy</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Amount</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Due Date</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
                  <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">Actions</th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {premiums.map((premium) => (
                  <tr key={premium.id.toString()} className="hover:bg-gray-50">
                    <td className="px-6 py-4">
                      <div className="flex flex-col">
                        <span className="text-sm font-medium text-gray-900">{premium.premium_number}</span>
                        <span className="text-sm text-gray-500">Installment #{premium.installment_number}</span>
                        <span className="text-xs text-gray-400 capitalize">
                          {premium.premium_frequency.replace('_', ' ')}
                        </span>
                      </div>
                    </td>
                    <td className="px-6 py-4">
                      <button
                        onClick={() => router.push(`/bancassurance/policies/${premium.policy_id}`)}
                        className="text-sm text-blue-600 hover:underline"
                      >
                        {premium.policy_number}
                      </button>
                    </td>
                    <td className="px-6 py-4">
                      <div className="flex flex-col">
                        <span className="text-sm font-medium text-gray-900">
                          {formatCurrency(premium.premium_amount)}
                        </span>
                        {premium.late_fee && premium.late_fee > 0 && (
                          <span className="text-xs text-red-600">
                            + {formatCurrency(premium.late_fee)} late fee
                          </span>
                        )}
                        {premium.discount_amount && premium.discount_amount > 0 && (
                          <span className="text-xs text-green-600">
                            - {formatCurrency(premium.discount_amount)} discount
                          </span>
                        )}
                      </div>
                    </td>
                    <td className="px-6 py-4">
                      <div className="flex flex-col">
                        <span className="text-sm text-gray-900">{formatDate(premium.premium_due_date)}</span>
                        {premium.premium_status === 'due' && (
                          <span className={`text-xs ${isOverdue(premium.premium_due_date) ? 'text-red-600' : 'text-gray-500'}`}>
                            {isOverdue(premium.premium_due_date) 
                              ? `${Math.abs(getDaysRemaining(premium.premium_due_date))} days overdue`
                              : `${getDaysRemaining(premium.premium_due_date)} days remaining`
                            }
                          </span>
                        )}
                        {premium.payment_date && (
                          <span className="text-xs text-green-600">
                            Paid: {formatDate(premium.payment_date)}
                          </span>
                        )}
                      </div>
                    </td>
                    <td className="px-6 py-4">
                      <PremiumStatusBadge status={premium.premium_status as PremiumStatus} />
                    </td>
                    <td className="px-6 py-4 text-right">
                      <div className="flex items-center justify-end gap-2">
                        {premium.premium_status === 'due' || premium.premium_status === 'overdue' ? (
                          <>
                            <button
                              onClick={() => handlePayment(premium)}
                              className="text-green-600 hover:text-green-900"
                              title="Record Payment"
                            >
                              <CheckCircle className="w-5 h-5" />
                            </button>
                            <button
                              onClick={() => handleWaive(premium)}
                              className="text-orange-600 hover:text-orange-900"
                              title="Waive Premium"
                            >
                              <XCircle className="w-5 h-5" />
                            </button>
                          </>
                        ) : (
                          <button
                            onClick={() => router.push(`/bancassurance/premiums/${premium.id}`)}
                            className="text-blue-600 hover:text-blue-900"
                          >
                            View Details
                          </button>
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
            Showing {(page - 1) * limit + 1} to {Math.min(page * limit, totalCount)} of {totalCount} premiums
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

      {/* Payment Modal */}
      {showPaymentModal && selectedPremium && (
        <PaymentModal
          premium={selectedPremium}
          onClose={() => {
            setShowPaymentModal(false)
            setSelectedPremium(null)
          }}
          onSuccess={() => {
            setShowPaymentModal(false)
            setSelectedPremium(null)
            loadPremiums()
          }}
        />
      )}
    </div>
  )
}

// Payment Modal Component
function PaymentModal({ 
  premium, 
  onClose, 
  onSuccess 
}: { 
  premium: InsurancePremium
  onClose: () => void
  onSuccess: () => void
}) {
  const [loading, setLoading] = useState(false)
  const [formData, setFormData] = useState({
    payment_date: new Date().toISOString().split('T')[0],
    payment_amount: premium.premium_amount,
    payment_method: 'online',
    payment_reference: '',
    transaction_id: '',
    collected_by_name: '',
    remarks: '',
  })

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    
    try {
      setLoading(true)
      await bancassuranceService.recordPremiumPayment(premium.id, {
        ...formData,
        payment_date: new Date(formData.payment_date).toISOString(),
      })
      alert('Payment recorded successfully!')
      onSuccess()
    } catch (error) {
      console.error('Failed to record payment:', error)
      alert('Failed to record payment')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg shadow-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
        <div className="p-6">
          <h2 className="text-2xl font-bold text-gray-900 mb-4">Record Premium Payment</h2>
          
          <div className="bg-blue-50 p-4 rounded-lg mb-6">
            <p className="text-sm text-gray-700">
              <strong>Premium:</strong> {premium.premium_number}
            </p>
            <p className="text-sm text-gray-700">
              <strong>Policy:</strong> {premium.policy_number}
            </p>
            <p className="text-sm text-gray-700">
              <strong>Amount Due:</strong> {formatCurrency(premium.premium_amount)}
            </p>
          </div>

          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Payment Date *</label>
                <input
                  type="date"
                  value={formData.payment_date}
                  onChange={(e) => setFormData({ ...formData, payment_date: e.target.value })}
                  required
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Payment Amount *</label>
                <input
                  type="number"
                  step="0.01"
                  value={formData.payment_amount}
                  onChange={(e) => setFormData({ ...formData, payment_amount: parseFloat(e.target.value) })}
                  required
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                />
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Payment Method *</label>
              <select
                value={formData.payment_method}
                onChange={(e) => setFormData({ ...formData, payment_method: e.target.value })}
                required
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
              >
                <option value="cash">Cash</option>
                <option value="cheque">Cheque</option>
                <option value="online">Online</option>
                <option value="neft">NEFT</option>
                <option value="rtgs">RTGS</option>
                <option value="upi">UPI</option>
              </select>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Payment Reference</label>
                <input
                  type="text"
                  value={formData.payment_reference}
                  onChange={(e) => setFormData({ ...formData, payment_reference: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Transaction ID</label>
                <input
                  type="text"
                  value={formData.transaction_id}
                  onChange={(e) => setFormData({ ...formData, transaction_id: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                />
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Collected By</label>
              <input
                type="text"
                value={formData.collected_by_name}
                onChange={(e) => setFormData({ ...formData, collected_by_name: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Remarks</label>
              <textarea
                value={formData.remarks}
                onChange={(e) => setFormData({ ...formData, remarks: e.target.value })}
                rows={3}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
              />
            </div>

            <div className="flex items-center justify-end gap-3 pt-4">
              <button
                type="button"
                onClick={onClose}
                className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50"
              >
                Cancel
              </button>
              <button
                type="submit"
                disabled={loading}
                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
              >
                {loading ? 'Recording...' : 'Record Payment'}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  )
}

// Components
function StatCard({ title, value, icon, color }: {
  title: string
  value: string
  icon: React.ReactNode
  color: 'blue' | 'green' | 'red' | 'yellow'
}) {
  const colorClasses = {
    blue: 'bg-blue-50 text-blue-600',
    green: 'bg-green-50 text-green-600',
    red: 'bg-red-50 text-red-600',
    yellow: 'bg-yellow-50 text-yellow-600',
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

function PremiumStatusBadge({ status }: { status: PremiumStatus }) {
  const color = PREMIUM_STATUS_COLORS[status]
  const label = PREMIUM_STATUS_LABELS[status]
  
  const colorClasses: Record<string, string> = {
    gray: 'bg-gray-100 text-gray-800',
    green: 'bg-green-100 text-green-800',
    yellow: 'bg-yellow-100 text-yellow-800',
    red: 'bg-red-100 text-red-800',
  }

  return (
    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${colorClasses[color]}`}>
      {label}
    </span>
  )
}

// Main export with Suspense wrapper
export default function PremiumsPage() {
  return (
    <Suspense fallback={
      <div className="min-h-screen bg-gray-50 p-6">
        <div className="flex items-center justify-center h-64">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
        </div>
      </div>
    }>
      <PremiumsContent />
    </Suspense>
  )
}
