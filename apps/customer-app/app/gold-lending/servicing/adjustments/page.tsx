'use client';

import { useState, useEffect } from 'react';
import { goldApi } from '../../goldApi';

interface LoanAdjustment {
  id: string;
  loan_account_id: string;
  loan_account_number?: string;
  adjustment_date: string;
  adjustment_type: string;
  adjustment_category: string;
  adjustment_amount: number;
  reason: string;
  approval_status: string;
  requested_by_user_id: string;
  approved_by_user_id?: string;
  approved_at?: string;
  rejection_reason?: string;
  created_at: string;
}

interface AdjustmentSummary {
  total_adjustments: number;
  pending_approval: number;
  approved_count: number;
  rejected_count: number;
  total_waiver: number;
  total_writeoff: number;
  total_reversal: number;
}

export default function AdjustmentsPage() {
  const [adjustments, setAdjustments] = useState<LoanAdjustment[]>([]);
  const [summary, setSummary] = useState<AdjustmentSummary | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  
  // Filters
  const [loanAccountId, setLoanAccountId] = useState('');
  const [adjustmentType, setAdjustmentType] = useState('');
  const [approvalStatus, setApprovalStatus] = useState('');

  // New Adjustment Form
  const [showForm, setShowForm] = useState(false);
  const [formData, setFormData] = useState({
    loan_account_id: '',
    adjustment_date: new Date().toISOString().split('T')[0],
    adjustment_type: 'waiver',
    adjustment_category: 'interest',
    adjustment_amount: '',
    reason: '',
    requested_by_user_id: 'user_001', // Mock user
  });

  useEffect(() => {
    loadAdjustments();
  }, [loanAccountId, adjustmentType, approvalStatus]);

  const loadAdjustments = async () => {
    try {
      setLoading(true);
      const filters: any = {};
      if (loanAccountId) filters.loan_account_id = loanAccountId;
      if (adjustmentType) filters.adjustment_type = adjustmentType;
      if (approvalStatus) filters.approval_status = approvalStatus;
      
      const data = await goldApi.getAdjustments(filters);
      setAdjustments(data);
      setError('');
    } catch (err: any) {
      setError(err.message || 'Failed to load adjustments');
      setAdjustments([]);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateAdjustment = async (e: React.FormEvent) => {
    e.preventDefault();
    
    try {
      setLoading(true);
      setError('');
      setSuccess('');

      const payload = {
        ...formData,
        adjustment_amount: parseFloat(formData.adjustment_amount),
      };

      await goldApi.createAdjustment(payload);
      setSuccess('Adjustment created successfully! Awaiting approval.');
      setShowForm(false);
      resetForm();
      loadAdjustments();
    } catch (err: any) {
      setError(err.message || 'Failed to create adjustment');
    } finally {
      setLoading(false);
    }
  };

  const handleApproveAdjustment = async (adjustmentId: string, status: 'approved' | 'rejected') => {
    const confirmMsg = status === 'approved' 
      ? 'Are you sure you want to approve this adjustment?'
      : 'Are you sure you want to reject this adjustment?';
    
    if (!confirm(confirmMsg)) return;

    let rejectionReason = '';
    if (status === 'rejected') {
      rejectionReason = prompt('Enter rejection reason:') || '';
      if (!rejectionReason) return;
    }

    try {
      setLoading(true);
      await goldApi.approveAdjustment(adjustmentId, 'user_001', status);
      setSuccess(`Adjustment ${status} successfully!`);
      loadAdjustments();
    } catch (err: any) {
      setError(err.message || `Failed to ${status} adjustment`);
    } finally {
      setLoading(false);
    }
  };

  const resetForm = () => {
    setFormData({
      loan_account_id: '',
      adjustment_date: new Date().toISOString().split('T')[0],
      adjustment_type: 'waiver',
      adjustment_category: 'interest',
      adjustment_amount: '',
      reason: '',
      requested_by_user_id: 'user_001',
    });
  };

  const getTypeBadgeClass = (type: string) => {
    const classes: Record<string, string> = {
      'waiver': 'bg-blue-100 text-blue-800',
      'write_off': 'bg-red-100 text-red-800',
      'reversal': 'bg-purple-100 text-purple-800',
      'correction': 'bg-yellow-100 text-yellow-800',
      'penalty': 'bg-orange-100 text-orange-800',
      'rebate': 'bg-green-100 text-green-800',
    };
    return classes[type] || 'bg-gray-100 text-gray-800';
  };

  const getCategoryBadge = (category: string) => {
    const classes: Record<string, string> = {
      'principal': 'bg-indigo-50 text-indigo-700',
      'interest': 'bg-purple-50 text-purple-700',
      'penalty': 'bg-red-50 text-red-700',
      'charges': 'bg-orange-50 text-orange-700',
    };
    return classes[category] || 'bg-gray-50 text-gray-700';
  };

  const getStatusBadgeClass = (status: string) => {
    const classes: Record<string, string> = {
      'pending': 'bg-yellow-100 text-yellow-800',
      'approved': 'bg-green-100 text-green-800',
      'rejected': 'bg-red-100 text-red-800',
    };
    return classes[status] || 'bg-gray-100 text-gray-800';
  };

  const formatAmount = (amount: number) => {
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR',
      maximumFractionDigits: 0,
    }).format(amount);
  };

  const formatDate = (dateStr: string) => {
    return new Date(dateStr).toLocaleDateString('en-IN', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
    });
  };

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">Loan Adjustments Management</h1>
              <p className="text-gray-600 mt-1">Waivers, write-offs, and corrections with maker-checker approval</p>
            </div>
            <button
              onClick={() => setShowForm(!showForm)}
              className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-medium"
            >
              {showForm ? 'Cancel' : '+ New Adjustment'}
            </button>
          </div>

          {/* Summary Cards */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
            <div className="bg-white rounded-lg shadow p-4">
              <div className="text-sm text-gray-600 mb-1">Total Adjustments</div>
              <div className="text-2xl font-bold text-gray-900">
                {adjustments.length}
              </div>
            </div>
            <div className="bg-yellow-50 rounded-lg shadow p-4">
              <div className="text-sm text-yellow-600 mb-1">Pending Approval</div>
              <div className="text-2xl font-bold text-yellow-900">
                {adjustments.filter(a => a.approval_status === 'pending').length}
              </div>
            </div>
            <div className="bg-green-50 rounded-lg shadow p-4">
              <div className="text-sm text-green-600 mb-1">Approved</div>
              <div className="text-2xl font-bold text-green-900">
                {adjustments.filter(a => a.approval_status === 'approved').length}
              </div>
            </div>
            <div className="bg-red-50 rounded-lg shadow p-4">
              <div className="text-sm text-red-600 mb-1">Rejected</div>
              <div className="text-2xl font-bold text-red-900">
                {adjustments.filter(a => a.approval_status === 'rejected').length}
              </div>
            </div>
          </div>

          {/* Amount Summary by Type */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
            <div className="bg-gradient-to-r from-blue-500 to-blue-600 rounded-lg shadow p-6 text-white">
              <div className="text-sm opacity-90 mb-2">Total Waivers</div>
              <div className="text-3xl font-bold">
                {formatAmount(
                  adjustments
                    .filter(a => a.adjustment_type === 'waiver' && a.approval_status === 'approved')
                    .reduce((sum, a) => sum + a.adjustment_amount, 0)
                )}
              </div>
            </div>
            <div className="bg-gradient-to-r from-red-500 to-red-600 rounded-lg shadow p-6 text-white">
              <div className="text-sm opacity-90 mb-2">Total Write-offs</div>
              <div className="text-3xl font-bold">
                {formatAmount(
                  adjustments
                    .filter(a => a.adjustment_type === 'write_off' && a.approval_status === 'approved')
                    .reduce((sum, a) => sum + a.adjustment_amount, 0)
                )}
              </div>
            </div>
            <div className="bg-gradient-to-r from-purple-500 to-purple-600 rounded-lg shadow p-6 text-white">
              <div className="text-sm opacity-90 mb-2">Total Reversals</div>
              <div className="text-3xl font-bold">
                {formatAmount(
                  adjustments
                    .filter(a => a.adjustment_type === 'reversal' && a.approval_status === 'approved')
                    .reduce((sum, a) => sum + a.adjustment_amount, 0)
                )}
              </div>
            </div>
          </div>
        </div>

        {/* New Adjustment Form */}
        {showForm && (
          <div className="bg-white rounded-lg shadow-sm p-6 mb-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Create New Adjustment</h2>
            <form onSubmit={handleCreateAdjustment}>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Loan Account ID *</label>
                  <input
                    type="text"
                    value={formData.loan_account_id}
                    onChange={(e) => setFormData({ ...formData, loan_account_id: e.target.value })}
                    required
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Adjustment Date *</label>
                  <input
                    type="date"
                    value={formData.adjustment_date}
                    onChange={(e) => setFormData({ ...formData, adjustment_date: e.target.value })}
                    required
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Adjustment Amount *</label>
                  <input
                    type="number"
                    step="0.01"
                    value={formData.adjustment_amount}
                    onChange={(e) => setFormData({ ...formData, adjustment_amount: e.target.value })}
                    required
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Adjustment Type *</label>
                  <select
                    value={formData.adjustment_type}
                    onChange={(e) => setFormData({ ...formData, adjustment_type: e.target.value })}
                    required
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  >
                    <option value="waiver">Waiver</option>
                    <option value="write_off">Write-off</option>
                    <option value="reversal">Reversal</option>
                    <option value="correction">Correction</option>
                    <option value="penalty">Penalty</option>
                    <option value="rebate">Rebate</option>
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Adjustment Category *</label>
                  <select
                    value={formData.adjustment_category}
                    onChange={(e) => setFormData({ ...formData, adjustment_category: e.target.value })}
                    required
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  >
                    <option value="principal">Principal</option>
                    <option value="interest">Interest</option>
                    <option value="penalty">Penalty</option>
                    <option value="charges">Charges</option>
                  </select>
                </div>
              </div>

              <div className="mb-4">
                <label className="block text-sm font-medium text-gray-700 mb-2">Reason *</label>
                <textarea
                  value={formData.reason}
                  onChange={(e) => setFormData({ ...formData, reason: e.target.value })}
                  required
                  rows={3}
                  placeholder="Provide detailed reason for this adjustment..."
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>

              <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4 mb-4">
                <div className="flex items-start">
                  <div className="text-yellow-600 mr-3">⚠️</div>
                  <div>
                    <p className="text-sm text-yellow-800 font-medium mb-1">Approval Required</p>
                    <p className="text-sm text-yellow-700">
                      This adjustment will be submitted for approval. It requires authorization from an approver before taking effect.
                    </p>
                  </div>
                </div>
              </div>

              <div className="flex justify-end gap-2">
                <button
                  type="button"
                  onClick={() => setShowForm(false)}
                  className="px-4 py-2 text-gray-700 bg-gray-100 rounded-lg hover:bg-gray-200 transition-colors"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={loading}
                  className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:bg-gray-400"
                >
                  {loading ? 'Submitting...' : 'Submit for Approval'}
                </button>
              </div>
            </form>
          </div>
        )}

        {/* Filters */}
        <div className="bg-white rounded-lg shadow-sm p-6 mb-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Filter Adjustments</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Loan Account ID</label>
              <input
                type="text"
                value={loanAccountId}
                onChange={(e) => setLoanAccountId(e.target.value)}
                placeholder="Enter loan account ID"
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Adjustment Type</label>
              <select
                value={adjustmentType}
                onChange={(e) => setAdjustmentType(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                <option value="">All Types</option>
                <option value="waiver">Waiver</option>
                <option value="write_off">Write-off</option>
                <option value="reversal">Reversal</option>
                <option value="correction">Correction</option>
                <option value="penalty">Penalty</option>
                <option value="rebate">Rebate</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Approval Status</label>
              <select
                value={approvalStatus}
                onChange={(e) => setApprovalStatus(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                <option value="">All Statuses</option>
                <option value="pending">Pending</option>
                <option value="approved">Approved</option>
                <option value="rejected">Rejected</option>
              </select>
            </div>
          </div>
        </div>

        {/* Success/Error Messages */}
        {success && (
          <div className="bg-green-50 border border-green-200 text-green-700 px-4 py-3 rounded-lg mb-6">
            {success}
          </div>
        )}
        {error && (
          <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg mb-6">
            {error}
          </div>
        )}

        {/* Adjustments Table */}
        <div className="bg-white rounded-lg shadow-sm overflow-hidden">
          {loading ? (
            <div className="p-12 text-center">
              <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
              <p className="mt-4 text-gray-600">Loading adjustments...</p>
            </div>
          ) : adjustments.length === 0 ? (
            <div className="p-12 text-center">
              <div className="text-gray-400 text-5xl mb-4">📝</div>
              <p className="text-gray-600 text-lg">No adjustments found</p>
              <p className="text-gray-500 text-sm mt-2">Create a new adjustment to get started</p>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Loan Account
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Date
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Type
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Category
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Amount
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Reason
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Status
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Actions
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {adjustments.map((adj) => (
                    <tr key={adj.id} className="hover:bg-gray-50 transition-colors">
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm font-medium text-gray-900">
                          {adj.loan_account_number || adj.loan_account_id}
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm text-gray-900">{formatDate(adj.adjustment_date)}</div>
                        {adj.approved_at && (
                          <div className="text-xs text-green-600">
                            Approved: {formatDate(adj.approved_at)}
                          </div>
                        )}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className={`px-2 py-1 text-xs font-medium rounded-full ${getTypeBadgeClass(adj.adjustment_type)}`}>
                          {adj.adjustment_type.replace('_', ' ').toUpperCase()}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className={`px-2 py-1 text-xs font-medium rounded-full ${getCategoryBadge(adj.adjustment_category)}`}>
                          {adj.adjustment_category.toUpperCase()}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm font-medium text-gray-900">
                          {formatAmount(adj.adjustment_amount)}
                        </div>
                      </td>
                      <td className="px-6 py-4">
                        <div className="text-sm text-gray-900 max-w-xs truncate" title={adj.reason}>
                          {adj.reason}
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className={`px-2 py-1 text-xs font-medium rounded-full ${getStatusBadgeClass(adj.approval_status)}`}>
                          {adj.approval_status.toUpperCase()}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium space-x-2">
                        {adj.approval_status === 'pending' && (
                          <>
                            <button
                              onClick={() => handleApproveAdjustment(adj.id, 'approved')}
                              className="text-green-600 hover:text-green-900"
                            >
                              Approve
                            </button>
                            <button
                              onClick={() => handleApproveAdjustment(adj.id, 'rejected')}
                              className="text-red-600 hover:text-red-900"
                            >
                              Reject
                            </button>
                          </>
                        )}
                        {adj.approval_status !== 'pending' && (
                          <span className="text-gray-400">-</span>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>

        {/* Adjustments Count */}
        {!loading && adjustments.length > 0 && (
          <div className="mt-4 text-center text-sm text-gray-600">
            Showing {adjustments.length} adjustment{adjustments.length !== 1 ? 's' : ''}
          </div>
        )}
      </div>
    </div>
  );
}
