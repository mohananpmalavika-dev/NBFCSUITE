'use client'

/**
 * Insurance Policy Details Page
 * Displays comprehensive policy information with actions
 */

import { useState, useEffect } from 'react'
import { useRouter, useParams } from 'next/navigation'
import { 
  ArrowLeft, FileText, User, DollarSign, Calendar, 
  CheckCircle, XCircle, AlertTriangle, RefreshCw,
  Download, Edit, MoreHorizontal
} from 'lucide-react'
import { bancassuranceService, type InsurancePolicy } from '@/services/bancassurance.service'
import { 
  POLICY_TYPE_LABELS, POLICY_STATUS_LABELS, PREMIUM_FREQUENCY_LABELS,
  POLICY_STATUS_COLORS, formatCurrency, formatDate 
} from '@/types/bancassurance'

export default function PolicyDetailsPage() {
  const router = useRouter()
  const params = useParams()
  const policyId = params.id as string

  const [policy, setPolicy] = useState<InsurancePolicy | null>(null)
  const [loading, setLoading] = useState(true)
  const [actionLoading, setActionLoading] = useState(false)

  useEffect(() => {
    loadPolicy()
  }, [policyId])

  const loadPolicy = async () => {
    try {
      setLoading(true)
      const response = await bancassuranceService.getPolicy(policyId)
      if (response.data.success) {
        setPolicy(response.data.data)
      }
    } catch (error) {
      console.error('Failed to load policy:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleActivate = async () => {
    if (!confirm('Activate this policy? This will generate the premium schedule.')) return
    
    try {
      setActionLoading(true)
      await bancassuranceService.activatePolicy(policyId)
      await loadPolicy()
      alert('Policy activated successfully!')
    } catch (error) {
      console.error('Failed to activate policy:', error)
      alert('Failed to activate policy')
    } finally {
      setActionLoading(false)
    }
  }

  const handleRevive = async () => {
    const arrearAmount = prompt('Enter arrear premium amount to be paid:')
    if (!arrearAmount) return

    try {
      setActionLoading(true)
      await bancassuranceService.revivePolicy(policyId, parseFloat(arrearAmount))
      await loadPolicy()
      alert('Policy revived successfully!')
    } catch (error) {
      console.error('Failed to revive policy:', error)
      alert('Failed to revive policy')
    } finally {
      setActionLoading(false)
    }
  }

  const handleSurrender = async () => {
    if (!confirm('Surrender this policy? This action cannot be undone.')) return

    try {
      setActionLoading(true)
      await bancassuranceService.surrenderPolicy(policyId)
      await loadPolicy()
      alert('Policy surrendered successfully!')
    } catch (error) {
      console.error('Failed to surrender policy:', error)
      alert('Failed to surrender policy')
    } finally {
      setActionLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    )
  }

  if (!policy) {
    return (
      <div className="flex flex-col items-center justify-center min-h-screen">
        <AlertTriangle className="w-16 h-16 text-red-500 mb-4" />
        <h2 className="text-2xl font-bold text-gray-900 mb-2">Policy Not Found</h2>
        <button
          onClick={() => router.back()}
          className="text-blue-600 hover:underline"
        >
          Go Back
        </button>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      {/* Header */}
      <div className="mb-6">
        <button
          onClick={() => router.back()}
          className="flex items-center gap-2 text-gray-600 hover:text-gray-900 mb-4"
        >
          <ArrowLeft className="w-5 h-5" />
          Back to Policies
        </button>

        <div className="flex items-start justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">{policy.policy_number}</h1>
            <p className="text-gray-600 mt-1">
              {POLICY_TYPE_LABELS[policy.policy_type as keyof typeof POLICY_TYPE_LABELS]} • {policy.insurance_company}
            </p>
          </div>
          
          <div className="flex items-center gap-3">
            <StatusBadge status={policy.policy_status} />
            {policy.is_lapsed && (
              <span className="px-3 py-1 bg-red-100 text-red-800 rounded-full text-sm font-medium">
                Lapsed
              </span>
            )}
          </div>
        </div>
      </div>

      {/* Action Buttons */}
      <div className="bg-white rounded-lg shadow-sm p-4 mb-6">
        <div className="flex items-center gap-3">
          {policy.policy_status === 'draft' && (
            <button
              onClick={handleActivate}
              disabled={actionLoading}
              className="flex items-center gap-2 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50"
            >
              <CheckCircle className="w-5 h-5" />
              Activate Policy
            </button>
          )}
          
          {policy.policy_status === 'lapsed' && (
            <button
              onClick={handleRevive}
              disabled={actionLoading}
              className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
            >
              <RefreshCw className="w-5 h-5" />
              Revive Policy
            </button>
          )}
          
          {policy.policy_status === 'active' && (
            <button
              onClick={handleSurrender}
              disabled={actionLoading}
              className="flex items-center gap-2 px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 disabled:opacity-50"
            >
              <XCircle className="w-5 h-5" />
              Surrender Policy
            </button>
          )}

          <button
            onClick={() => router.push(`/bancassurance/premiums?policy_id=${policy.id}`)}
            className="flex items-center gap-2 px-4 py-2 bg-white border border-gray-300 rounded-lg hover:bg-gray-50"
          >
            <DollarSign className="w-5 h-5" />
            View Premiums
          </button>

          <button
            onClick={() => router.push(`/bancassurance/claims/new?policy_id=${policy.id}`)}
            className="flex items-center gap-2 px-4 py-2 bg-white border border-gray-300 rounded-lg hover:bg-gray-50"
          >
            <FileText className="w-5 h-5" />
            Register Claim
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Main Info */}
        <div className="lg:col-span-2 space-y-6">
          {/* Policy Details */}
          <InfoCard title="Policy Details" icon={<FileText className="w-5 h-5" />}>
            <InfoRow label="Policy Number" value={policy.policy_number} />
            <InfoRow label="Policy Type" value={POLICY_TYPE_LABELS[policy.policy_type as keyof typeof POLICY_TYPE_LABELS]} />
            <InfoRow label="Insurance Company" value={policy.insurance_company} />
            <InfoRow label="Product Name" value={policy.product_name} />
            <InfoRow label="Channel" value={policy.channel} />
            {policy.agent_name && (
              <InfoRow label="Agent" value={`${policy.agent_name} (${policy.agent_code})`} />
            )}
          </InfoCard>

          {/* Customer & Insured */}
          <InfoCard title="Customer & Insured Information" icon={<User className="w-5 h-5" />}>
            <InfoRow label="Customer" value={policy.customer_name} />
            <InfoRow label="Insured Name" value={policy.insured_name} />
            <InfoRow label="Date of Birth" value={formatDate(policy.insured_dob)} />
            <InfoRow label="Age" value={`${policy.insured_age} years`} />
            {policy.insured_gender && (
              <InfoRow label="Gender" value={policy.insured_gender} />
            )}
            {policy.nominee_name && (
              <>
                <InfoRow label="Nominee" value={policy.nominee_name} />
                <InfoRow label="Relationship" value={policy.nominee_relationship || 'N/A'} />
              </>
            )}
          </InfoCard>

          {/* Coverage Details */}
          <InfoCard title="Coverage Details" icon={<DollarSign className="w-5 h-5" />}>
            <InfoRow label="Sum Assured" value={formatCurrency(policy.sum_assured)} highlight />
            <InfoRow label="Policy Term" value={`${policy.policy_term_years} years`} />
            <InfoRow label="Premium Paying Term" value={`${policy.premium_paying_term_years} years`} />
            <InfoRow label="Premium Amount" value={formatCurrency(policy.premium_amount)} />
            <InfoRow label="Premium Frequency" value={PREMIUM_FREQUENCY_LABELS[policy.premium_frequency as keyof typeof PREMIUM_FREQUENCY_LABELS]} />
            {policy.surrender_value && (
              <InfoRow label="Surrender Value" value={formatCurrency(policy.surrender_value)} />
            )}
            {policy.maturity_value && (
              <InfoRow label="Maturity Value" value={formatCurrency(policy.maturity_value)} />
            )}
          </InfoCard>

          {/* Important Dates */}
          <InfoCard title="Important Dates" icon={<Calendar className="w-5 h-5" />}>
            <InfoRow label="Policy Start Date" value={formatDate(policy.policy_start_date)} />
            <InfoRow label="Policy End Date" value={formatDate(policy.policy_end_date)} />
            <InfoRow label="First Premium Date" value={formatDate(policy.first_premium_date)} />
            {policy.next_premium_due_date && (
              <InfoRow label="Next Premium Due" value={formatDate(policy.next_premium_due_date)} highlight />
            )}
            {policy.maturity_date && (
              <InfoRow label="Maturity Date" value={formatDate(policy.maturity_date)} />
            )}
            {policy.lapsed_date && (
              <InfoRow label="Lapsed Date" value={formatDate(policy.lapsed_date)} />
            )}
          </InfoCard>
        </div>

        {/* Sidebar */}
        <div className="space-y-6">
          {/* Financial Summary */}
          <div className="bg-white rounded-lg shadow-sm p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Financial Summary</h3>
            <div className="space-y-4">
              <div>
                <p className="text-sm text-gray-600">Total Premium Paid</p>
                <p className="text-2xl font-bold text-green-600">{formatCurrency(policy.total_premium_paid)}</p>
              </div>
              <div>
                <p className="text-sm text-gray-600">Outstanding Premium</p>
                <p className="text-2xl font-bold text-red-600">{formatCurrency(policy.outstanding_premium)}</p>
              </div>
              <div className="border-t pt-4">
                <p className="text-sm text-gray-600">Premiums Paid</p>
                <p className="text-lg font-semibold">{policy.premiums_paid_count} of {policy.premiums_due_count + policy.premiums_paid_count}</p>
              </div>
            </div>
          </div>

          {/* Quick Actions */}
          <div className="bg-white rounded-lg shadow-sm p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Quick Actions</h3>
            <div className="space-y-2">
              <ActionButton 
                label="View All Premiums"
                onClick={() => router.push(`/bancassurance/premiums?policy_id=${policy.id}`)}
              />
              <ActionButton 
                label="Payment History"
                onClick={() => router.push(`/bancassurance/premiums?policy_id=${policy.id}&status=paid`)}
              />
              <ActionButton 
                label="View Claims"
                onClick={() => router.push(`/bancassurance/claims?policy_id=${policy.id}`)}
              />
              <ActionButton 
                label="Commission Details"
                onClick={() => router.push(`/bancassurance/commissions?policy_id=${policy.id}`)}
              />
            </div>
          </div>

          {/* Remarks */}
          {policy.remarks && (
            <div className="bg-white rounded-lg shadow-sm p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-2">Remarks</h3>
              <p className="text-sm text-gray-600">{policy.remarks}</p>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

// Components
function StatusBadge({ status }: { status: string }) {
  const color = POLICY_STATUS_COLORS[status as keyof typeof POLICY_STATUS_COLORS] || 'gray'
  const label = POLICY_STATUS_LABELS[status as keyof typeof POLICY_STATUS_LABELS] || status
  
  const colorClasses: Record<string, string> = {
    gray: 'bg-gray-100 text-gray-800',
    green: 'bg-green-100 text-green-800',
    orange: 'bg-orange-100 text-orange-800',
    red: 'bg-red-100 text-red-800',
    blue: 'bg-blue-100 text-blue-800',
    purple: 'bg-purple-100 text-purple-800',
  }

  return (
    <span className={`px-3 py-1 rounded-full text-sm font-medium ${colorClasses[color]}`}>
      {label}
    </span>
  )
}

function InfoCard({ title, icon, children }: { 
  title: string
  icon: React.ReactNode
  children: React.ReactNode 
}) {
  return (
    <div className="bg-white rounded-lg shadow-sm p-6">
      <div className="flex items-center gap-2 mb-4">
        <div className="text-blue-600">{icon}</div>
        <h3 className="text-lg font-semibold text-gray-900">{title}</h3>
      </div>
      <div className="space-y-3">
        {children}
      </div>
    </div>
  )
}

function InfoRow({ label, value, highlight = false }: { 
  label: string
  value: string
  highlight?: boolean 
}) {
  return (
    <div className="flex justify-between items-center py-2 border-b border-gray-100 last:border-0">
      <span className="text-sm text-gray-600">{label}</span>
      <span className={`text-sm font-medium ${highlight ? 'text-blue-600' : 'text-gray-900'}`}>
        {value}
      </span>
    </div>
  )
}

function ActionButton({ label, onClick }: { label: string; onClick: () => void }) {
  return (
    <button
      onClick={onClick}
      className="w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-50 rounded-lg transition-colors"
    >
      {label}
    </button>
  )
}
