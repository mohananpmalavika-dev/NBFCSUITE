'use client';

import { useState, useEffect } from 'react';
import { goldApi } from '../../goldApi';

interface LoanPrepayment {
  id: string;
  loan_account_id: string;
  loan_account_number?: string;
  prepayment_date: string;
  prepayment_type: string;
  prepayment_amount: number;
  principal_reduced: number;
  interest_waived: number;
  prepayment_charges: number;
  outstanding_after_prepayment: number;
  prepayment_status: string;
  approved_by_user_id?: string;
  approved_at?: string;
  created_at: string;
}

interface PrepaymentSummary {
  total_prepayments: number;
  pending_approval: number;
  approved_count: number;
  total_prepayment_amount: number;
  total_principal_reduced: number;
  total_charges_collected: number;
}

export default function PrepaymentsPage() {
  const [prepayments, setPrepayments] = useState<LoanPrepayment[]>([]);
  const [summary, setSummary] = useState<PrepaymentSummary | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  
  // Filters
  const [loanAccountId, setLoanAccountId] = useState('');
  const [prepaymentType, setPrepaymentType] = useState('');
  const [prepaymentStatus, setPrepaymentStatus] = useState('');

  // New Prepayment Form
  const [showForm, setShowForm] = useState(false);
  const [formData, setFormData] = useState({
    loan_account_id: '',
    prepayment_date: new Date().toISOString().split('T')[0],
    prepayment_type: 'part_payment',
    prepayment_amount: '',
    principal_reduced: '',
    interest_waived: '',
    prepayment_charges: '',
    outstanding_after_prepayment: '',
    created_by_user_id: 'user_001',
  });

  useEffect(() => {
    loadPrepayments();
  }, [loanAccountId, prepaymentType, prepaymentStatus]);

  const loadPrepayments = async () => {
    try {
      setLoading(true);
      const filters: any = {};
      if (loanAccountId) filters.loan_account_id = loanAccountId;
      if (prepaymentType) filters.prepayment_type = prepaymentType;
      if (prepaymentStatus) filters.prepayment_status = prepaymentStatus;
      
      const data = await goldApi.getPrepayments(filters);
      setPrepayments(data);
      setError('');
    } catch (err: any) {
      setError(err.message || 'Failed to load prepayments');
      setPrepayments([]);
    } finally {
      setLoading(false);
    }
  };

  const handleCreatePrepayment = async (e: React.FormEvent) => {
    e.preventDefault();
    
    try {
      setLoading(true);
      setError('');
      setSuccess('');

      const payload = {
        ...formData,
        prepayment_amount: parseFloat(formData.prepayment_amount),
        principal_reduced: parseFloat(formData.principal_reduced),
        interest_waived: parseFloat(formData.interest_waived || '0'),
        prepayment_charges: parseFloat(formData.prepayment_charges || '0'),
        outstanding_after_prepayment: parseFloat(formData.outstanding_after_prepayment),
      };

      await goldApi.createPrepayment(payload);
      setSuccess('Prepayment created successfully! Awaiting approval.');
      setShowForm(false);
      resetForm();
      loadPrepayments();
    } catch (err: any) {
      setError(err.message || 'Failed to create prepayment');
    } finally {
      setLoading(false);
    }
  };

  const handleApprovePrepayment = async (prepaymentId: string) => {
    if (!confirm('Are you sure you want to approve this prepayment?')) return;

    try {
      setLoading(true);
      await goldApi.approvePrepayment(prepaymentId, 'user_001');
      setSuccess('Prepayment approved successfully!');
      loadPrepayments();
    } catch (err: any) {
      setError(err.message || 'Failed to approve prepayment');
    } finally {
      setLoading(false);
    }
  };

  const resetForm = () => {
    setFormData({
      loan_account_id: '',
      prepayment_date: new Date().toISOString().split('T')[0],
      prepayment_type: 'part_payment',
      prepayment_amount: '',
      principal_reduced: '',
      interest_waived: '',
      prepayment_charges: '',
      outstanding_after_prepayment: '',
      created_by_user_id: 'user_001',
    });
  };

  const getTypeBadgeClass = (type: string) => {
    const classes: Record<string, string> = {
      'part_payment': 'bg-blue-100 text-blue-800',
      'foreclosure': 'bg-red-100 text-red-800',
      'full_prepayment': 'bg-green-100 text-green-800',
    };
    return classes[type] || 'bg-gray-100 text-gray-800';
  };

  const getStatusBadgeClass = (status: string) => {
    const classes: Record<string, string> = {
      'pending': 'bg-yellow-100 text-yellow-800',
      'approved': 'bg-green-100 text-green-800',
      'rejected': 'bg-red-100 text-red-800',
      'completed': 'bg-purple-100 text-purple-800',
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
              <h1 className="text-3xl font-bold text-gray-900">Prepayment & Foreclosure</h1>
              <p className="text-gray-600 mt-1">Manage part payments, foreclosures, and early settlements</p>
            </div>
            <button
              onClick={() => setShowForm(!showForm)}
              className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-medium"
            >
              {showForm ? 'Cancel' : '+ New Prepayment'}
            </button>
          </div>

          {/* Summary Cards */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
            <div className="bg-white rounded-lg shadow p-4">
              <div className="text-sm text-gray-600 mb-1">Total Prepayments</div>
              <div className="text-2xl font-bold text-gray-900">{prepayments.length}</div>
            </div>
            <div className="bg-yellow-50 rounded-lg shadow p-4">
              <div className="text-sm text-yellow-600 mb-1">Pending Approval</div>
              <div className="text-2xl font-bold text-yellow-900">
                {prepayments.filter(p => p.prepayment_status === 'pending').length}
              </div>
            </div>
            <div className="bg-green-50 rounded-lg shadow p-4">
              <div className="text-sm text-green-600 mb-1">Approved</div>
              <div className="text-2xl font-bold text-green-900">
                {prepayments.filter(p => p.prepayment_status === 'approved').length}
              </div>
            </div>
          </div>

          {/* Amount Summary */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
            <div className="bg-gradient-to-r from-blue-500 to-blue-600 rounded-lg shadow p-6 text-white">
              <div className="text-sm opacity-90 mb-2">Total Prepayment Amount</div>
              <div className="text-3xl font-bold">
                {formatAmount(prepayments.reduce((sum, p) => sum + p.prepayment_amount, 0))}
              </div>
            </div>
            <div className="bg-gradient-to-r from-green-500 to-green-600 rounded-lg shadow p-6 text-white">
              <div className="text-sm opacity-90 mb-2">Principal Reduced</div>
              <div className="text-3xl font-bold">
                {formatAmount(prepayments.reduce((sum, p) => sum + p.principal_reduced, 0))}
              </div>
            </div>
            <div className="bg-gradient-to-r from-purple-500 to-purple-600 rounded-lg shadow p-6 text-white">
              <div className="text-sm opacity-90 mb-2">Charges Collected</div>
              <div className="text-3xl font-bold">
                {formatAmount(prepayments.reduce((sum, p) => sum + p.prepayment_charges, 0))}
              </div>
            </div>
          </div>
        </div>

        {/* New Prepayment Form */}
        {showForm && (
          <div className="bg-white rounded-lg shadow-sm p-6 mb-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Create New Prepayment</h2>
            <form onSubmit={handleCreatePrepayment}>
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
                  <label className="block text-sm font-medium text-gray-700 mb-2">Prepayment Date *</label>
                  <input
                    type="date"
                    value={formData.prepayment_date}
                    onChange={(e) => setFormData({ ...formData, prepayment_date: e.target.value })}
                    required
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Prepayment Type *</label>
                  <select
                    value={formData.prepayment_type}
                    onChange={(e) => setFormData({ ...formData, prepayment_type: e.target.value })}
                    required
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  >
                    <option value="part_payment">Part Payment</option>
                    <option value="foreclosure">Foreclosure</option>
                    <option value="full_prepayment">Full Prepayment</option>
                  </select>
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Prepayment Amount *</label>
                  <input
                    type="number"
                    step="0.01"
                    value={formData.prepayment_amount}
                    onChange={(e) => setFormData({ ...formData, prepayment_amount: e.target.value })}
                    required
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Principal Reduced *</label>
                  <input
                    type="number"
                    step="0.01"
                    value={formData.principal_reduced}
                    onChange={(e) => setFormData({ ...formData, principal_reduced: e.target.value })}
                    required
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Interest Waived</label>
                  <input
                    type="number"
                    step="0.01"
                    value={formData.interest_waived}
                    onChange={(e) => setFormData({ ...formData, interest_waived: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Prepayment Charges</label>
                  <input
                    type="number"
                    step="0.01"
                    value={formData.prepayment_charges}
                    onChange={(e) => setFormData({ ...formData, prepayment_charges: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Outstanding After *</label>
                  <input
                    type="number"
                    step="0.01"
                    value={formData.outstanding_after_prepayment}
                    onChange={(e) => setFormData({ ...formData, outstanding_after_prepayment: e.target.value })}
                    required
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
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
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Filter Prepayments</h2>
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
              <label className="block text-sm font-medium text-gray-700 mb-2">Prepayment Type</label>
              <select
                value={prepaymentType}
                onChange={(e) => setPrepaymentType(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                <option value="">All Types</option>
                <option value="part_payment">Part Payment</option>
                <option value="foreclosure">Foreclosure</option>
                <option value="full_prepayment">Full Prepayment</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Status</label>
              <select
                value={prepaymentStatus}
                onChange={(e) => setPrepaymentStatus(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                <option value="">All Statuses</option>
                <option value="pending">Pending</option>
                <option value="approved">Approved</option>
                <option value="rejected">Rejected</option>
                <option value="completed">Completed</option>
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

        {/* Prepayments Table */}
        <div className="bg-white rounded-lg shadow-sm overflow-hidden">
          {loading ? (
            <div className="p-12 text-center">
              <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
              <p className="mt-4 text-gray-600">Loading prepayments...</p>
            </div>
          ) : prepayments.length === 0 ? (
            <div className="p-12 text-center">
              <div className="text-gray-400 text-5xl mb-4">💸</div>
              <p className="text-gray-600 text-lg">No prepayments found</p>
              <p className="text-gray-500 text-sm mt-2">Create a new prepayment to get started</p>
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
                      Amount
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Principal Reduced
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Charges
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Outstanding After
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
                  {prepayments.map((prep) => (
                    <tr key={prep.id} className="hover:bg-gray-50 transition-colors">
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm font-medium text-gray-900">
                          {prep.loan_account_number || prep.loan_account_id}
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm text-gray-900">{formatDate(prep.prepayment_date)}</div>
                        {prep.approved_at && (
                          <div className="text-xs text-green-600">
                            Approved: {formatDate(prep.approved_at)}
                          </div>
                        )}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className={`px-2 py-1 text-xs font-medium rounded-full ${getTypeBadgeClass(prep.prepayment_type)}`}>
                          {prep.prepayment_type.replace('_', ' ').toUpperCase()}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                        {formatAmount(prep.prepayment_amount)}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-green-600">
                        {formatAmount(prep.principal_reduced)}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600">
                        {formatAmount(prep.prepayment_charges)}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-orange-600 font-medium">
                        {formatAmount(prep.outstanding_after_prepayment)}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className={`px-2 py-1 text-xs font-medium rounded-full ${getStatusBadgeClass(prep.prepayment_status)}`}>
                          {prep.prepayment_status.toUpperCase()}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                        {prep.prepayment_status === 'pending' && (
                          <button
                            onClick={() => handleApprovePrepayment(prep.id)}
                            className="text-green-600 hover:text-green-900"
                          >
                            Approve
                          </button>
                        )}
                        {prep.prepayment_status !== 'pending' && (
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

        {/* Prepayments Count */}
        {!loading && prepayments.length > 0 && (
          <div className="mt-4 text-center text-sm text-gray-600">
            Showing {prepayments.length} prepayment{prepayments.length !== 1 ? 's' : ''}
          </div>
        )}
      </div>
    </div>
  );
}
