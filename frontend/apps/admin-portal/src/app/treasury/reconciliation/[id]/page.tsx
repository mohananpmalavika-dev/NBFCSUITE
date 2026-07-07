'use client'

/**
 * Bank Reconciliation Detail Page
 * View reconciliation details with items
 */

import { useState, useEffect } from 'react'
import { useRouter, useParams } from 'next/navigation'
import { reconciliationService } from '@/services/treasury.service'
import type { 
  BankReconciliationDetail, 
  ReconciliationItem,
  ReconciliationStatus 
} from '@/services/treasury.service'

export default function ReconciliationDetailPage() {
  const router = useRouter()
  const params = useParams()
  const reconciliationId = parseInt(params.id as string)
  
  const [reconciliation, setReconciliation] = useState<BankReconciliationDetail | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [actionLoading, setActionLoading] = useState(false)

  useEffect(() => {
    fetchReconciliation()
  }, [reconciliationId])

  const fetchReconciliation = async () => {
    try {
      setLoading(true)
      const data = await reconciliationService.getReconciliation(reconciliationId)
      setReconciliation(data)
    } catch (err: any) {
      setError(err.message || 'Failed to fetch reconciliation')
    } finally {
      setLoading(false)
    }
  }

  const handleSubmitForApproval = async () => {
    if (!confirm('Submit this reconciliation for approval?')) return
    
    try {
      setActionLoading(true)
      await reconciliationService.submitForApproval(reconciliationId)
      await fetchReconciliation()
      alert('Reconciliation submitted for approval')
    } catch (err: any) {
      alert(err.message || 'Failed to submit')
    } finally {
      setActionLoading(false)
    }
  }

  const handleApprove = async () => {
    const notes = prompt('Approval notes (optional):')
    if (notes === null) return
    
    try {
      setActionLoading(true)
      await reconciliationService.approveReconciliation(reconciliationId, notes)
      await fetchReconciliation()
      alert('Reconciliation approved successfully')
    } catch (err: any) {
      alert(err.message || 'Failed to approve')
    } finally {
      setActionLoading(false)
    }
  }

  const handleReject = async () => {
    const notes = prompt('Rejection reason (required):')
    if (!notes) return
    
    try {
      setActionLoading(true)
      await reconciliationService.rejectReconciliation(reconciliationId, notes)
      await fetchReconciliation()
      alert('Reconciliation rejected')
    } catch (err: any) {
      alert(err.message || 'Failed to reject')
    } finally {
      setActionLoading(false)
    }
  }

  const getStatusBadge = (status: ReconciliationStatus) => {
    const styles: Record<ReconciliationStatus, string> = {
      draft: 'bg-gray-100 text-gray-800',
      in_progress: 'bg-blue-100 text-blue-800',
      matched: 'bg-green-100 text-green-800',
      pending_approval: 'bg-yellow-100 text-yellow-800',
      approved: 'bg-emerald-100 text-emerald-800',
      rejected: 'bg-red-100 text-red-800'
    }
    
    return (
      <span className={`px-3 py-1 rounded-full text-sm font-medium ${styles[status]}`}>
        {status.replace('_', ' ').toUpperCase()}
      </span>
    )
  }

  const getItemTypeBadge = (type: string) => {
    const styles: Record<string, string> = {
      outstanding_cheque: 'bg-orange-100 text-orange-800',
      deposit_in_transit: 'bg-blue-100 text-blue-800',
      bank_charges: 'bg-red-100 text-red-800',
      interest_earned: 'bg-green-100 text-green-800',
      direct_debit: 'bg-purple-100 text-purple-800',
      direct_credit: 'bg-teal-100 text-teal-800',
      error_correction: 'bg-yellow-100 text-yellow-800',
      other: 'bg-gray-100 text-gray-800'
    }
    
    return (
      <span className={`px-2 py-1 rounded text-xs font-medium ${styles[type] || styles.other}`}>
        {type.replace(/_/g, ' ').toUpperCase()}
      </span>
    )
  }

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR',
      minimumFractionDigits: 2
    }).format(amount)
  }

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-IN')
  }

  if (loading) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="bg-white rounded-lg shadow p-8 text-center">
          <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
          <p className="text-gray-600 mt-2">Loading reconciliation...</p>
        </div>
      </div>
    )
  }

  if (error || !reconciliation) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg">
          {error || 'Reconciliation not found'}
        </div>
      </div>
    )
  }

  return (
    <div className="container mx-auto px-4 py-8">

      {/* Header */}
      <div className="flex justify-between items-center mb-6">
        <div>
          <button
            onClick={() => router.back()}
            className="text-blue-600 hover:text-blue-800 mb-2"
          >
            ← Back to List
          </button>
          <h1 className="text-3xl font-bold text-gray-900">
            Reconciliation Details
          </h1>
          <p className="text-gray-600 mt-1">{reconciliation.reconciliation_number}</p>
        </div>
        <div className="flex gap-3">
          {reconciliation.status === 'draft' && (
            <>
              <button
                onClick={() => router.push(`/treasury/reconciliation/${reconciliationId}/edit`)}
                className="bg-gray-600 text-white px-6 py-2 rounded-lg hover:bg-gray-700"
                disabled={actionLoading}
              >
                Edit
              </button>
              <button
                onClick={handleSubmitForApproval}
                className="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700"
                disabled={actionLoading}
              >
                Submit for Approval
              </button>
            </>
          )}
          {reconciliation.status === 'pending_approval' && (
            <>
              <button
                onClick={handleReject}
                className="bg-red-600 text-white px-6 py-2 rounded-lg hover:bg-red-700"
                disabled={actionLoading}
              >
                Reject
              </button>
              <button
                onClick={handleApprove}
                className="bg-green-600 text-white px-6 py-2 rounded-lg hover:bg-green-700"
                disabled={actionLoading}
              >
                Approve
              </button>
            </>
          )}
        </div>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-6">
        <div className="bg-white rounded-lg shadow p-6">
          <div className="text-sm text-gray-600 mb-1">Book Balance</div>
          <div className="text-2xl font-bold text-gray-900">
            {formatCurrency(reconciliation.book_balance)}
          </div>
        </div>
        <div className="bg-white rounded-lg shadow p-6">
          <div className="text-sm text-gray-600 mb-1">Bank Balance</div>
          <div className="text-2xl font-bold text-gray-900">
            {formatCurrency(reconciliation.bank_balance)}
          </div>
        </div>
        <div className="bg-white rounded-lg shadow p-6">
          <div className="text-sm text-gray-600 mb-1">Difference</div>
          <div className={`text-2xl font-bold ${
            reconciliation.difference === 0 ? 'text-green-600' : 'text-red-600'
          }`}>
            {formatCurrency(Math.abs(reconciliation.difference))}
          </div>
        </div>
        <div className="bg-white rounded-lg shadow p-6">
          <div className="text-sm text-gray-600 mb-1">Status</div>
          <div className="mt-2">
            {getStatusBadge(reconciliation.status)}
          </div>
        </div>
      </div>

      {/* Details Section */}
      <div className="bg-white rounded-lg shadow mb-6">
        <div className="px-6 py-4 border-b border-gray-200">
          <h2 className="text-xl font-bold text-gray-900">Reconciliation Information</h2>
        </div>
        <div className="p-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Reconciliation Date
              </label>
              <div className="text-gray-900">
                {formatDate(reconciliation.reconciliation_date)}
              </div>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Bank Account ID
              </label>
              <div className="text-gray-900">{reconciliation.bank_account_id}</div>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Period Start Date
              </label>
              <div className="text-gray-900">
                {formatDate(reconciliation.period_start_date)}
              </div>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Period End Date
              </label>
              <div className="text-gray-900">
                {formatDate(reconciliation.period_end_date)}
              </div>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Matched Items
              </label>
              <div className="text-gray-900">
                {reconciliation.total_matched} ({formatCurrency(reconciliation.matched_amount)})
              </div>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Unmatched Items
              </label>
              <div className="text-gray-900">
                {reconciliation.total_unmatched} ({formatCurrency(reconciliation.unmatched_amount)})
              </div>
            </div>
            {reconciliation.notes && (
              <div className="md:col-span-2">
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Notes
                </label>
                <div className="text-gray-900">{reconciliation.notes}</div>
              </div>
            )}
            {reconciliation.approval_notes && (
              <div className="md:col-span-2">
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Approval Notes
                </label>
                <div className="text-gray-900">{reconciliation.approval_notes}</div>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Reconciliation Items */}
      <div className="bg-white rounded-lg shadow">
        <div className="px-6 py-4 border-b border-gray-200 flex justify-between items-center">
          <h2 className="text-xl font-bold text-gray-900">Reconciliation Items</h2>
          <div className="text-sm text-gray-600">
            {reconciliation.items.length} items
          </div>
        </div>
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                  Date
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                  Type
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                  Description
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                  Reference
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                  Amount
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                  Debit/Credit
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                  Status
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {reconciliation.items.length === 0 ? (
                <tr>
                  <td colSpan={7} className="px-6 py-8 text-center text-gray-500">
                    No items found
                  </td>
                </tr>
              ) : (
                reconciliation.items.map((item) => (
                  <tr key={item.id} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {formatDate(item.item_date)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      {getItemTypeBadge(item.item_type)}
                    </td>
                    <td className="px-6 py-4 text-sm text-gray-900">
                      {item.description}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {item.reference_number || '-'}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                      {formatCurrency(item.amount)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm">
                      <span className={`px-2 py-1 rounded text-xs font-medium ${
                        item.is_debit 
                          ? 'bg-red-100 text-red-800' 
                          : 'bg-green-100 text-green-800'
                      }`}>
                        {item.is_debit ? 'Debit' : 'Credit'}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm">
                      <span className={`px-2 py-1 rounded text-xs font-medium ${
                        item.is_matched 
                          ? 'bg-green-100 text-green-800' 
                          : 'bg-yellow-100 text-yellow-800'
                      }`}>
                        {item.is_matched ? 'Matched' : 'Unmatched'}
                      </span>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Timestamps */}
      <div className="mt-6 bg-gray-50 rounded-lg p-4 text-sm text-gray-600">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div>
            <span className="font-medium">Created:</span> {formatDate(reconciliation.created_at)}
          </div>
          <div>
            <span className="font-medium">Updated:</span> {formatDate(reconciliation.updated_at)}
          </div>
          {reconciliation.approved_at && (
            <div>
              <span className="font-medium">Approved:</span> {formatDate(reconciliation.approved_at)}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
