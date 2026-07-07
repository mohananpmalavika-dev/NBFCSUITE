'use client'

/**
 * Fund Transfer Detail Page
 * View transfer details with workflow actions
 */

import { useState, useEffect } from 'react'
import { useRouter, useParams } from 'next/navigation'
import { fundTransferService } from '@/services/treasury.service'
import type { FundTransfer, FundTransferStatus, FundTransferType } from '@/services/treasury.service'

export default function FundTransferDetailPage() {
  const router = useRouter()
  const params = useParams()
  const transferId = parseInt(params.id as string)
  
  const [transfer, setTransfer] = useState<FundTransfer | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [actionLoading, setActionLoading] = useState(false)

  useEffect(() => {
    fetchTransfer()
  }, [transferId])

  const fetchTransfer = async () => {
    try {
      setLoading(true)
      const data = await fundTransferService.getTransfer(transferId)
      setTransfer(data)
    } catch (err: any) {
      setError(err.message || 'Failed to fetch transfer')
    } finally {
      setLoading(false)
    }
  }

  const handleSubmitForApproval = async () => {
    if (!confirm('Submit this transfer for approval?')) return
    
    try {
      setActionLoading(true)
      await fundTransferService.submitForApproval(transferId)
      await fetchTransfer()
      alert('Transfer submitted for approval')
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
      await fundTransferService.approveTransfer(transferId, notes)
      await fetchTransfer()
      alert('Transfer approved successfully')
    } catch (err: any) {
      alert(err.message || 'Failed to approve')
    } finally {
      setActionLoading(false)
    }
  }

  const handleReject = async () => {
    const reason = prompt('Rejection reason (required):')
    if (!reason) return
    
    try {
      setActionLoading(true)
      await fundTransferService.rejectTransfer(transferId, reason)
      await fetchTransfer()
      alert('Transfer rejected')
    } catch (err: any) {
      alert(err.message || 'Failed to reject')
    } finally {
      setActionLoading(false)
    }
  }

  const handleExecute = async () => {
    if (!confirm('Execute this transfer? This will move the funds.')) return
    
    const transRef = prompt('Transaction reference (optional):')
    if (transRef === null) return
    
    try {
      setActionLoading(true)
      await fundTransferService.executeTransfer(transferId, transRef)
      await fetchTransfer()
      alert('Transfer executed successfully')
    } catch (err: any) {
      alert(err.message || 'Failed to execute transfer')
    } finally {
      setActionLoading(false)
    }
  }

  const handleCancel = async () => {
    const reason = prompt('Cancellation reason (required):')
    if (!reason) return
    
    if (!confirm('Cancel this transfer?')) return
    
    try {
      setActionLoading(true)
      await fundTransferService.cancelTransfer(transferId, reason)
      await fetchTransfer()
      alert('Transfer cancelled')
    } catch (err: any) {
      alert(err.message || 'Failed to cancel')
    } finally {
      setActionLoading(false)
    }
  }

  const getStatusBadge = (status: FundTransferStatus) => {
    const styles: Record<FundTransferStatus, string> = {
      draft: 'bg-gray-100 text-gray-800',
      pending_approval: 'bg-yellow-100 text-yellow-800',
      approved: 'bg-blue-100 text-blue-800',
      rejected: 'bg-red-100 text-red-800',
      scheduled: 'bg-purple-100 text-purple-800',
      in_progress: 'bg-orange-100 text-orange-800',
      completed: 'bg-green-100 text-green-800',
      failed: 'bg-red-100 text-red-800',
      cancelled: 'bg-gray-100 text-gray-800'
    }
    
    return (
      <span className={`px-3 py-1 rounded-full text-sm font-medium ${styles[status]}`}>
        {status.replace('_', ' ').toUpperCase()}
      </span>
    )
  }

  const getTypeLabel = (type: FundTransferType) => {
    const labels: Record<FundTransferType, string> = {
      internal: 'Internal Transfer',
      neft: 'NEFT',
      rtgs: 'RTGS',
      imps: 'IMPS',
      upi: 'UPI',
      cheque: 'Cheque',
      demand_draft: 'Demand Draft'
    }
    return labels[type]
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

  const formatDateTime = (dateString: string) => {
    return new Date(dateString).toLocaleString('en-IN')
  }

  if (loading) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="bg-white rounded-lg shadow p-8 text-center">
          <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
          <p className="text-gray-600 mt-2">Loading transfer...</p>
        </div>
      </div>
    )
  }

  if (error || !transfer) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg">
          {error || 'Transfer not found'}
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
            Transfer Details
          </h1>
          <p className="text-gray-600 mt-1">{transfer.transfer_number}</p>
        </div>
        <div className="flex gap-3">
          {transfer.status === 'draft' && (
            <>
              <button
                onClick={() => router.push(`/treasury/fund-transfers/${transferId}/edit`)}
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
          {transfer.status === 'pending_approval' && (
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
          {(transfer.status === 'approved' || transfer.status === 'scheduled') && (
            <button
              onClick={handleExecute}
              className="bg-green-600 text-white px-6 py-2 rounded-lg hover:bg-green-700"
              disabled={actionLoading}
            >
              Execute Transfer
            </button>
          )}
          {transfer.status !== 'completed' && transfer.status !== 'cancelled' && (
            <button
              onClick={handleCancel}
              className="bg-gray-600 text-white px-6 py-2 rounded-lg hover:bg-gray-700"
              disabled={actionLoading}
            >
              Cancel
            </button>
          )}
        </div>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
        <div className="bg-white rounded-lg shadow p-6">
          <div className="text-sm text-gray-600 mb-1">Transfer Amount</div>
          <div className="text-2xl font-bold text-gray-900">
            {formatCurrency(transfer.amount)}
          </div>
          <div className="text-xs text-gray-500 mt-1">{transfer.currency}</div>
        </div>
        <div className="bg-white rounded-lg shadow p-6">
          <div className="text-sm text-gray-600 mb-1">Transfer Type</div>
          <div className="text-xl font-bold text-gray-900">
            {getTypeLabel(transfer.transfer_type)}
          </div>
        </div>
        <div className="bg-white rounded-lg shadow p-6">
          <div className="text-sm text-gray-600 mb-1">Status</div>
          <div className="mt-2">
            {getStatusBadge(transfer.status)}
          </div>
        </div>
      </div>

      {/* Transfer Details */}
      <div className="bg-white rounded-lg shadow mb-6">
        <div className="px-6 py-4 border-b border-gray-200">
          <h2 className="text-xl font-bold text-gray-900">Transfer Information</h2>
        </div>
        <div className="p-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Transfer Date
              </label>
              <div className="text-gray-900">{formatDate(transfer.transfer_date)}</div>
            </div>
            {transfer.is_scheduled && transfer.scheduled_date && (
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Scheduled Date
                </label>
                <div className="text-purple-600 font-medium">{formatDate(transfer.scheduled_date)}</div>
              </div>
            )}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Source Account
              </label>
              <div className="text-gray-900">
                {transfer.source_account_number || `Account ID: ${transfer.source_account_id}`}
              </div>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Destination {transfer.transfer_type === 'internal' ? 'Account' : 'Details'}
              </label>
              <div className="text-gray-900">
                {transfer.transfer_type === 'internal' ? (
                  transfer.destination_account_id ? `Account ID: ${transfer.destination_account_id}` : '-'
                ) : (
                  <div>
                    <div>{transfer.destination_account_holder}</div>
                    <div className="text-sm text-gray-600">{transfer.destination_account_number}</div>
                    <div className="text-sm text-gray-600">{transfer.destination_bank_name}</div>
                    <div className="text-sm text-gray-600">IFSC: {transfer.destination_ifsc}</div>
                  </div>
                )}
              </div>
            </div>
            <div className="md:col-span-2">
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Purpose
              </label>
              <div className="text-gray-900">{transfer.purpose}</div>
            </div>
            {transfer.reference_number && (
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Reference Number
                </label>
                <div className="text-gray-900">{transfer.reference_number}</div>
              </div>
            )}
            {transfer.transaction_reference && (
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Transaction Reference
                </label>
                <div className="text-gray-900">{transfer.transaction_reference}</div>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Approval/Rejection Details */}
      {(transfer.approved_at || transfer.rejected_at) && (
        <div className="bg-white rounded-lg shadow mb-6">
          <div className="px-6 py-4 border-b border-gray-200">
            <h2 className="text-xl font-bold text-gray-900">
              {transfer.approved_at ? 'Approval' : 'Rejection'} Details
            </h2>
          </div>
          <div className="p-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {transfer.approved_at && (
                <>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Approved At
                    </label>
                    <div className="text-gray-900">{formatDateTime(transfer.approved_at)}</div>
                  </div>
                  {transfer.approval_notes && (
                    <div className="md:col-span-2">
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        Approval Notes
                      </label>
                      <div className="text-gray-900">{transfer.approval_notes}</div>
                    </div>
                  )}
                </>
              )}
              {transfer.rejected_at && (
                <>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Rejected At
                    </label>
                    <div className="text-gray-900">{formatDateTime(transfer.rejected_at)}</div>
                  </div>
                  {transfer.rejection_reason && (
                    <div className="md:col-span-2">
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        Rejection Reason
                      </label>
                      <div className="text-red-600">{transfer.rejection_reason}</div>
                    </div>
                  )}
                </>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Execution Details */}
      {(transfer.executed_at || transfer.failure_reason) && (
        <div className="bg-white rounded-lg shadow mb-6">
          <div className="px-6 py-4 border-b border-gray-200">
            <h2 className="text-xl font-bold text-gray-900">Execution Details</h2>
          </div>
          <div className="p-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {transfer.executed_at && (
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Executed At
                  </label>
                  <div className="text-gray-900">{formatDateTime(transfer.executed_at)}</div>
                </div>
              )}
              {transfer.failure_reason && (
                <div className="md:col-span-2">
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Failure Reason
                  </label>
                  <div className="text-red-600">{transfer.failure_reason}</div>
                  <div className="text-sm text-gray-600 mt-1">
                    Retry Count: {transfer.retry_count}
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Notes */}
      {transfer.notes && (
        <div className="bg-white rounded-lg shadow mb-6">
          <div className="px-6 py-4 border-b border-gray-200">
            <h2 className="text-xl font-bold text-gray-900">Notes</h2>
          </div>
          <div className="p-6">
            <div className="text-gray-900">{transfer.notes}</div>
          </div>
        </div>
      )}

      {/* Timestamps */}
      <div className="mt-6 bg-gray-50 rounded-lg p-4 text-sm text-gray-600">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div>
            <span className="font-medium">Created:</span> {formatDateTime(transfer.created_at)}
          </div>
          <div>
            <span className="font-medium">Updated:</span> {formatDateTime(transfer.updated_at)}
          </div>
        </div>
      </div>
    </div>
  )
}
