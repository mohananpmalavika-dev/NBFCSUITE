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
