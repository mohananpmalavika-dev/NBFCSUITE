'use client';

import { useState, useEffect } from 'react';
import { useRouter, useParams } from 'next/navigation';
import { settlementApi } from '@/lib/api/collection';
import { SettlementProposal } from '@/types/collection';

export default function SettlementDetailPage() {
  const router = useRouter();
  const params = useParams();
  const proposalId = params.id as string;

  const [proposal, setProposal] = useState<SettlementProposal | null>(null);
  const [loading, setLoading] = useState(true);
  const [actionLoading, setActionLoading] = useState(false);
  const [approvalNotes, setApprovalNotes] = useState('');
  const [showApprovalModal, setShowApprovalModal] = useState(false);
  const [approvalAction, setApprovalAction] = useState<'approve' | 'reject'>('approve');

  useEffect(() => {
    loadProposal();
  }, [proposalId]);

  const loadProposal = async () => {
    try {
      setLoading(true);
      const data = await settlementApi.getProposal(proposalId);
      setProposal(data);
    } catch (error) {
      console.error('Failed to load proposal:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleApprovalAction = async () => {
    if (!proposal) return;

    setActionLoading(true);
    try {
      if (approvalAction === 'approve') {
        await settlementApi.approveProposal(proposal.id, approvalNotes);
      } else {
        await settlementApi.rejectProposal(proposal.id, approvalNotes);
      }
      setShowApprovalModal(false);
      loadProposal();
    } catch (error) {
      console.error('Failed to process approval:', error);
      alert('Failed to process approval action');
    } finally {
      setActionLoading(false);
    }
  };

  const handleRecordPayment = async () => {
    if (!proposal) return;
    router.push(`/collections/settlement/${proposal.id}/payment`);
  };

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR',
      maximumFractionDigits: 0,
    }).format(amount);
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-IN', {
      day: '2-digit',
      month: 'short',
      year: 'numeric',
    });
  };

  const getStatusColor = (status: string) => {
    const colors: Record<string, string> = {
      draft: 'bg-gray-100 text-gray-800',
      pending_approval: 'bg-yellow-100 text-yellow-800',
      approved: 'bg-green-100 text-green-800',
      rejected: 'bg-red-100 text-red-800',
      payment_pending: 'bg-blue-100 text-blue-800',
      completed: 'bg-purple-100 text-purple-800',
      cancelled: 'bg-gray-100 text-gray-800',
    };
    return colors[status] || 'bg-gray-100 text-gray-800';
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-gray-500">Loading proposal details...</div>
      </div>
    );
  }

  if (!proposal) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <p className="text-gray-500 mb-4">Proposal not found</p>
          <button
            onClick={() => router.push('/collections/settlement')}
            className="text-blue-600 hover:text-blue-700"
          >
            Back to Settlements
          </button>
        </div>
      </div>
    );
  }

  const discount = ((proposal.original_outstanding - proposal.settlement_amount) / proposal.original_outstanding) * 100;

  return (
    <div className="max-w-6xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex justify-between items-start">
        <div>
          <button
            onClick={() => router.push('/collections/settlement')}
            className="text-blue-600 hover:text-blue-700 mb-2 flex items-center gap-1"
          >
            ← Back to Settlements
          </button>
          <h1 className="text-2xl font-bold text-gray-900">
            Settlement Proposal {proposal.proposal_number}
          </h1>
          <p className="text-gray-600 mt-1">Loan: {proposal.loan_account_id}</p>
        </div>
        <div className="flex gap-3">
          <span className={`px-4 py-2 rounded-lg text-sm font-medium ${getStatusColor(proposal.status)}`}>
            {proposal.status.replace('_', ' ').toUpperCase()}
          </span>
        </div>
      </div>

      {/* Action Buttons */}
      {proposal.status === 'pending_approval' && (
        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="font-semibold text-yellow-900">Pending Approval</h3>
              <p className="text-sm text-yellow-700 mt-1">
                This proposal requires approval before proceeding
              </p>
            </div>
            <div className="flex gap-3">
              <button
                onClick={() => {
                  setApprovalAction('reject');
                  setShowApprovalModal(true);
                }}
                className="px-4 py-2 bg-white text-red-600 border border-red-300 rounded-lg hover:bg-red-50"
              >
                Reject
              </button>
              <button
                onClick={() => {
                  setApprovalAction('approve');
                  setShowApprovalModal(true);
                }}
                className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700"
              >
                Approve
              </button>
            </div>
          </div>
        </div>
      )}

      {proposal.status === 'approved' && (
        <div className="bg-green-50 border border-green-200 rounded-lg p-4">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="font-semibold text-green-900">Approved - Awaiting Payment</h3>
              <p className="text-sm text-green-700 mt-1">
                Settlement approved on {formatDate(proposal.approved_at!)}
              </p>
            </div>
            <button
              onClick={handleRecordPayment}
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
            >
              Record Payment
            </button>
          </div>
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Main Content - Left Side */}
        <div className="lg:col-span-2 space-y-6">
          {/* Customer & Loan Details */}
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Customer & Loan Details</h2>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <p className="text-sm text-gray-600">Customer Name</p>
                <p className="font-medium text-gray-900">{proposal.customer_name || 'N/A'}</p>
              </div>
              <div>
                <p className="text-sm text-gray-600">Customer Contact</p>
                <p className="font-medium text-gray-900">{proposal.customer_contact || 'N/A'}</p>
              </div>
              <div>
                <p className="text-sm text-gray-600">Loan Account ID</p>
                <p className="font-medium text-gray-900">{proposal.loan_account_id}</p>
              </div>
              <div>
                <p className="text-sm text-gray-600">Created By</p>
                <p className="font-medium text-gray-900">{proposal.created_by}</p>
              </div>
            </div>
          </div>

          {/* Outstanding Breakdown */}
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Outstanding Amount Breakdown</h2>
            <div className="space-y-3">
              <div className="flex justify-between items-center pb-2 border-b">
                <span className="text-gray-600">Principal Outstanding</span>
                <span className="font-medium">{formatCurrency(proposal.principal_outstanding)}</span>
              </div>
              <div className="flex justify-between items-center pb-2 border-b">
                <span className="text-gray-600">Interest Outstanding</span>
                <span className="font-medium">{formatCurrency(proposal.interest_outstanding)}</span>
              </div>
              <div className="flex justify-between items-center pb-2 border-b">
                <span className="text-gray-600">Penalty Outstanding</span>
                <span className="font-medium">{formatCurrency(proposal.penalty_outstanding)}</span>
              </div>
              <div className="flex justify-between items-center pb-2 border-b">
                <span className="text-gray-600">Other Charges</span>
                <span className="font-medium">{formatCurrency(proposal.other_charges)}</span>
              </div>
              <div className="flex justify-between items-center pt-2 text-lg">
                <span className="font-semibold text-gray-900">Total Outstanding</span>
                <span className="font-bold text-gray-900">
                  {formatCurrency(proposal.original_outstanding)}
                </span>
              </div>
            </div>
          </div>

          {/* Settlement Terms */}
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Settlement Terms</h2>
            <div className="space-y-4">
              <div className="bg-green-50 rounded-lg p-4">
                <div className="flex justify-between items-center mb-2">
                  <span className="text-green-900 font-semibold">Settlement Amount</span>
                  <span className="text-2xl font-bold text-green-600">
                    {formatCurrency(proposal.settlement_amount)}
                  </span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-green-700">Waiver Amount</span>
                  <span className="text-green-700 font-medium">
                    {formatCurrency(proposal.waiver_amount)} ({discount.toFixed(1)}% discount)
                  </span>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <p className="text-sm text-gray-600">Payment Terms</p>
                  <p className="font-medium text-gray-900 capitalize">
                    {proposal.payment_terms.replace('_', ' ')}
                  </p>
                </div>
                {proposal.payment_terms === 'installments' && (
                  <>
                    <div>
                      <p className="text-sm text-gray-600">Number of Installments</p>
                      <p className="font-medium text-gray-900">
                        {proposal.number_of_installments}
                      </p>
                    </div>
                    <div>
                      <p className="text-sm text-gray-600">Frequency</p>
                      <p className="font-medium text-gray-900 capitalize">
                        {proposal.installment_frequency}
                      </p>
                    </div>
                  </>
                )}
                {proposal.valid_until && (
                  <div>
                    <p className="text-sm text-gray-600">Valid Until</p>
                    <p className="font-medium text-red-600">
                      {formatDate(proposal.valid_until)}
                    </p>
                  </div>
                )}
              </div>
            </div>
          </div>

          {/* NPV Analysis */}
          {proposal.npv_analysis && (
            <div className="bg-white rounded-lg shadow p-6">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">NPV Analysis</h2>
              <div className="grid grid-cols-3 gap-4">
                <div className="bg-purple-50 rounded-lg p-4">
                  <p className="text-sm text-purple-700">NPV Without Settlement</p>
                  <p className="text-xl font-bold text-purple-900">
                    {formatCurrency(proposal.npv_analysis.npv_without_settlement)}
                  </p>
                </div>
                <div className="bg-purple-50 rounded-lg p-4">
                  <p className="text-sm text-purple-700">NPV With Settlement</p>
                  <p className="text-xl font-bold text-purple-900">
                    {formatCurrency(proposal.npv_analysis.npv_with_settlement)}
                  </p>
                </div>
                <div className={`rounded-lg p-4 ${proposal.npv_analysis.npv_benefit > 0 ? 'bg-green-50' : 'bg-red-50'}`}>
                  <p className={`text-sm ${proposal.npv_analysis.npv_benefit > 0 ? 'text-green-700' : 'text-red-700'}`}>
                    NPV Benefit
                  </p>
                  <p className={`text-xl font-bold ${proposal.npv_analysis.npv_benefit > 0 ? 'text-green-900' : 'text-red-900'}`}>
                    {formatCurrency(proposal.npv_analysis.npv_benefit)}
                  </p>
                </div>
              </div>
              <div className="grid grid-cols-3 gap-4 mt-4">
                <div>
                  <p className="text-sm text-gray-600">Est. Recovery Time</p>
                  <p className="font-medium text-gray-900">
                    {proposal.npv_analysis.estimated_recovery_time} months
                  </p>
                </div>
                <div>
                  <p className="text-sm text-gray-600">Est. Recovery Amount</p>
                  <p className="font-medium text-gray-900">
                    {formatCurrency(proposal.npv_analysis.estimated_recovery_amount)}
                  </p>
                </div>
                <div>
                  <p className="text-sm text-gray-600">Discount Rate</p>
                  <p className="font-medium text-gray-900">
                    {proposal.npv_analysis.discount_rate}%
                  </p>
                </div>
              </div>
            </div>
          )}

          {/* Justification */}
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Justification</h2>
            <div className="space-y-4">
              <div>
                <p className="text-sm font-medium text-gray-700 mb-2">Reason</p>
                <p className="text-gray-900">{proposal.reason}</p>
              </div>
              {proposal.justification && (
                <div>
                  <p className="text-sm font-medium text-gray-700 mb-2">Detailed Justification</p>
                  <p className="text-gray-900 whitespace-pre-wrap">{proposal.justification}</p>
                </div>
              )}
              {proposal.internal_notes && (
                <div>
                  <p className="text-sm font-medium text-gray-700 mb-2">Internal Notes</p>
                  <p className="text-gray-600 whitespace-pre-wrap">{proposal.internal_notes}</p>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Sidebar - Right Side */}
        <div className="space-y-6">
          {/* Timeline */}
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Timeline</h2>
            <div className="space-y-4">
              <div className="flex items-start gap-3">
                <div className="w-2 h-2 bg-blue-600 rounded-full mt-2"></div>
                <div className="flex-1">
                  <p className="text-sm font-medium text-gray-900">Created</p>
                  <p className="text-xs text-gray-600">{formatDate(proposal.created_at)}</p>
                  <p className="text-xs text-gray-500">by {proposal.created_by}</p>
                </div>
              </div>
              {proposal.approved_at && (
                <div className="flex items-start gap-3">
                  <div className="w-2 h-2 bg-green-600 rounded-full mt-2"></div>
                  <div className="flex-1">
                    <p className="text-sm font-medium text-gray-900">Approved</p>
                    <p className="text-xs text-gray-600">{formatDate(proposal.approved_at)}</p>
                    {proposal.approved_by && (
                      <p className="text-xs text-gray-500">by {proposal.approved_by}</p>
                    )}
                  </div>
                </div>
              )}
              {proposal.rejected_at && (
                <div className="flex items-start gap-3">
                  <div className="w-2 h-2 bg-red-600 rounded-full mt-2"></div>
                  <div className="flex-1">
                    <p className="text-sm font-medium text-gray-900">Rejected</p>
                    <p className="text-xs text-gray-600">{formatDate(proposal.rejected_at)}</p>
                    {proposal.rejected_by && (
                      <p className="text-xs text-gray-500">by {proposal.rejected_by}</p>
                    )}
                  </div>
                </div>
              )}
              {proposal.completed_at && (
                <div className="flex items-start gap-3">
                  <div className="w-2 h-2 bg-purple-600 rounded-full mt-2"></div>
                  <div className="flex-1">
                    <p className="text-sm font-medium text-gray-900">Completed</p>
                    <p className="text-xs text-gray-600">{formatDate(proposal.completed_at)}</p>
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* Approval Notes */}
          {(proposal.approval_notes || proposal.rejection_reason) && (
            <div className="bg-white rounded-lg shadow p-6">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">
                {proposal.approval_notes ? 'Approval Notes' : 'Rejection Reason'}
              </h2>
              <p className="text-gray-700 whitespace-pre-wrap">
                {proposal.approval_notes || proposal.rejection_reason}
              </p>
            </div>
          )}
        </div>
      </div>

      {/* Approval Modal */}
      {showApprovalModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 max-w-md w-full mx-4">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">
              {approvalAction === 'approve' ? 'Approve Settlement' : 'Reject Settlement'}
            </h3>
            <div className="mb-4">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                {approvalAction === 'approve' ? 'Approval Notes' : 'Rejection Reason'}
              </label>
              <textarea
                value={approvalNotes}
                onChange={(e) => setApprovalNotes(e.target.value)}
                rows={4}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder={`Enter ${approvalAction === 'approve' ? 'approval notes' : 'rejection reason'}...`}
              />
            </div>
            <div className="flex justify-end gap-3">
              <button
                onClick={() => {
                  setShowApprovalModal(false);
                  setApprovalNotes('');
                }}
                className="px-4 py-2 text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50"
                disabled={actionLoading}
              >
                Cancel
              </button>
              <button
                onClick={handleApprovalAction}
                className={`px-4 py-2 text-white rounded-lg ${
                  approvalAction === 'approve'
                    ? 'bg-green-600 hover:bg-green-700'
                    : 'bg-red-600 hover:bg-red-700'
                }`}
                disabled={actionLoading}
              >
                {actionLoading ? 'Processing...' : approvalAction === 'approve' ? 'Approve' : 'Reject'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
