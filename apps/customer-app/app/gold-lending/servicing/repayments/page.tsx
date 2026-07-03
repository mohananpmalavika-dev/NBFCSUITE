'use client';

import { useState, useEffect } from 'react';
import { goldApi } from '../../goldApi';

interface RepaymentTransaction {
  id: string;
  loan_account_id: string;
  loan_account_number?: string;
  transaction_date: string;
  payment_mode: string;
  amount_paid: number;
  principal_paid: number;
  interest_paid: number;
  penalty_paid: number;
  other_charges_paid: number;
  transaction_reference: string;
  transaction_status: string;
  payment_source?: string;
  created_by_user_id: string;
  verified_by_user_id?: string;
  verified_at?: string;
  reversal_reason?: string;
  created_at: string;
}

interface RepaymentSummary {
  total_repayments: number;
  total_amount: number;
  total_principal: number;
  total_interest: number;
  total_penalty: number;
  pending_verification: number;
  completed_count: number;
  reversed_count: number;
}

export default function RepaymentsPage() {
  const [repayments, setRepayments] = useState<RepaymentTransaction[]>([]);
  const [summary, setSummary] = useState<RepaymentSummary | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  
  // Filters
  const [loanAccountId, setLoanAccountId] = useState('');
  const [paymentMode, setPaymentMode] = useState('');
  const [transactionStatus, setTransactionStatus] = useState('');
  const [dateFrom, setDateFrom] = useState('');
  const [dateTo, setDateTo] = useState('');

  // New Repayment Form
  const [showForm, setShowForm] = useState(false);
  const [formData, setFormData] = useState({
    loan_account_id: '',
    transaction_date: new Date().toISOString().split('T')[0],
    payment_mode: 'cash',
    amount_paid: '',
    principal_paid: '',
    interest_paid: '',
    penalty_paid: '',
    other_charges_paid: '',
    transaction_reference: '',
    payment_source: '',
    created_by_user_id: 'user_001', // Mock user
  });

  useEffect(() => {
    if (loanAccountId) {
      loadRepayments();
      loadSummary();
    }
  }, [loanAccountId, paymentMode, transactionStatus, dateFrom, dateTo]);

  const loadRepayments = async () => {
    if (!loanAccountId) return;

    try {
      setLoading(true);
      const filters: any = { loan_account_id: loanAccountId };
      if (paymentMode) filters.payment_mode = paymentMode;
      if (transactionStatus) filters.transaction_status = transactionStatus;
      if (dateFrom) filters.from_date = dateFrom;
      if (dateTo) filters.to_date = dateTo;
      
      const data = await goldApi.getRepayments(filters);
      setRepayments(data);
      setError('');
    } catch (err: any) {
      setError(err.message || 'Failed to load repayments');
      setRepayments([]);
    } finally {
      setLoading(false);
    }
  };

  const loadSummary = async () => {
    if (!loanAccountId) return;

    try {
      const data = await goldApi.getRepaymentSummary(loanAccountId);
      setSummary(data);
    } catch (err) {
      console.error('Failed to load summary:', err);
    }
  };

  const handleCreateRepayment = async (e: React.FormEvent) => {
    e.preventDefault();
    
    try {
      setLoading(true);
      setError('');
      setSuccess('');

      const payload = {
        ...formData,
        amount_paid: parseFloat(formData.amount_paid),
        principal_paid: parseFloat(formData.principal_paid || '0'),
        interest_paid: parseFloat(formData.interest_paid || '0'),
        penalty_paid: parseFloat(formData.penalty_paid || '0'),
        other_charges_paid: parseFloat(formData.other_charges_paid || '0'),
      };

      await goldApi.createRepayment(payload);
      setSuccess('Repayment created successfully!');
      setShowForm(false);
      resetForm();
      loadRepayments();
      loadSummary();
    } catch (err: any) {
      setError(err.message || 'Failed to create repayment');
    } finally {
      setLoading(false);
    }
  };

  const handleVerifyRepayment = async (transactionId: string) => {
    if (!confirm('Are you sure you want to verify this repayment?')) return;

    try {
      setLoading(true);
      await goldApi.verifyRepayment(transactionId, 'user_001');
      setSuccess('Repayment verified successfully!');
      loadRepayments();
    } catch (err: any) {
      setError(err.message || 'Failed to verify repayment');
    } finally {
      setLoading(false);
    }
  };

  const handleReverseRepayment = async (transactionId: string) => {
    const reason = prompt('Enter reversal reason:');
    if (!reason) return;

    try {
      setLoading(true);
      await goldApi.reverseRepayment(transactionId, 'user_001', reason);
      setSuccess('Repayment reversed successfully!');
      loadRepayments();
      loadSummary();
    } catch (err: any) {
      setError(err.message || 'Failed to reverse repayment');
    } finally {
      setLoading(false);
    }
  };

  const resetForm = () => {
    setFormData({
      loan_account_id: loanAccountId || '',
      transaction_date: new Date().toISOString().split('T')[0],
      payment_mode: 'cash',
      amount_paid: '',
      principal_paid: '',
      interest_paid: '',
      penalty_paid: '',
      other_charges_paid: '',
      transaction_reference: '',
      payment_source: '',
      created_by_user_id: 'user_001',
    });
  };

  const getStatusBadgeClass = (status: string) => {
    const classes: Record<string, string> = {
      'pending': 'bg-yellow-100 text-yellow-800',
      'completed': 'bg-green-100 text-green-800',
      'bounced': 'bg-red-100 text-red-800',
      'reversed': 'bg-gray-100 text-gray-800',
      'cancelled': 'bg-gray-100 text-gray-800',
    };
    return classes[status] || 'bg-gray-100 text-gray-800';
  };

  const getPaymentModeBadge = (mode: string) => {
    const classes: Record<string, string> = {
      'cash': 'bg-green-50 text-green-700',
      'cheque': 'bg-blue-50 text-blue-700',
      'neft': 'bg-purple-50 text-purple-700',
      'imps': 'bg-indigo-50 text-indigo-700',
      'rtgs': 'bg-pink-50 text-pink-700',
      'upi': 'bg-orange-50 text-orange-700',
      'auto_debit': 'bg-teal-50 text-teal-700',
      'adjustment': 'bg-gray-50 text-gray-700',
    };
    return classes[mode] || 'bg-gray-50 text-gray-700';
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
              <h1 className="text-3xl font-bold text-gray-900">Repayment Collections</h1>
              <p className="text-gray-600 mt-1">Record and manage loan repayments</p>
            </div>
            <button
              onClick={() => setShowForm(!showForm)}
              className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-medium"
            >
              {showForm ? 'Cancel' : '+ Record Payment'}
            </button>
          </div>

          {/* Summary Cards */}
          {summary && (
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
              <div className="bg-white rounded-lg shadow p-4">
                <div className="text-sm text-gray-600 mb-1">Total Repayments</div>
                <div className="text-2xl font-bold text-gray-900">{summary.total_repayments}</div>
              </div>
              <div className="bg-green-50 rounded-lg shadow p-4">
                <div className="text-sm text-green-600 mb-1">Completed</div>
                <div className="text-2xl font-bold text-green-900">{summary.completed_count}</div>
              </div>
              <div className="bg-yellow-50 rounded-lg shadow p-4">
                <div className="text-sm text-yellow-600 mb-1">Pending Verification</div>
                <div className="text-2xl font-bold text-yellow-900">{summary.pending_verification}</div>
              </div>
              <div className="bg-gray-50 rounded-lg shadow p-4">
                <div className="text-sm text-gray-600 mb-1">Reversed</div>
                <div className="text-2xl font-bold text-gray-900">{summary.reversed_count}</div>
              </div>
            </div>
          )}

          {/* Amount Summary */}
          {summary && (
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
              <div className="bg-gradient-to-r from-blue-500 to-blue-600 rounded-lg shadow p-6 text-white">
                <div className="text-sm opacity-90 mb-2">Total Amount</div>
                <div className="text-3xl font-bold">{formatAmount(summary.total_amount)}</div>
              </div>
              <div className="bg-gradient-to-r from-green-500 to-green-600 rounded-lg shadow p-6 text-white">
                <div className="text-sm opacity-90 mb-2">Principal Paid</div>
                <div className="text-3xl font-bold">{formatAmount(summary.total_principal)}</div>
              </div>
              <div className="bg-gradient-to-r from-purple-500 to-purple-600 rounded-lg shadow p-6 text-white">
                <div className="text-sm opacity-90 mb-2">Interest Paid</div>
                <div className="text-3xl font-bold">{formatAmount(summary.total_interest)}</div>
              </div>
              <div className="bg-gradient-to-r from-red-500 to-red-600 rounded-lg shadow p-6 text-white">
                <div className="text-sm opacity-90 mb-2">Penalty Paid</div>
                <div className="text-3xl font-bold">{formatAmount(summary.total_penalty)}</div>
              </div>
            </div>
          )}
        </div>

        {/* New Repayment Form */}
        {showForm && (
          <div className="bg-white rounded-lg shadow-sm p-6 mb-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Record New Payment</h2>
            <form onSubmit={handleCreateRepayment}>
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
                  <label className="block text-sm font-medium text-gray-700 mb-2">Transaction Date *</label>
                  <input
                    type="date"
                    value={formData.transaction_date}
                    onChange={(e) => setFormData({ ...formData, transaction_date: e.target.value })}
                    required
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Payment Mode *</label>
                  <select
                    value={formData.payment_mode}
                    onChange={(e) => setFormData({ ...formData, payment_mode: e.target.value })}
                    required
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  >
                    <option value="cash">Cash</option>
                    <option value="cheque">Cheque</option>
                    <option value="neft">NEFT</option>
                    <option value="imps">IMPS</option>
                    <option value="rtgs">RTGS</option>
                    <option value="upi">UPI</option>
                    <option value="auto_debit">Auto Debit</option>
                  </select>
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Amount Paid *</label>
                  <input
                    type="number"
                    step="0.01"
                    value={formData.amount_paid}
                    onChange={(e) => setFormData({ ...formData, amount_paid: e.target.value })}
                    required
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Principal Paid</label>
                  <input
                    type="number"
                    step="0.01"
                    value={formData.principal_paid}
                    onChange={(e) => setFormData({ ...formData, principal_paid: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Interest Paid</label>
                  <input
                    type="number"
                    step="0.01"
                    value={formData.interest_paid}
                    onChange={(e) => setFormData({ ...formData, interest_paid: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Penalty Paid</label>
                  <input
                    type="number"
                    step="0.01"
                    value={formData.penalty_paid}
                    onChange={(e) => setFormData({ ...formData, penalty_paid: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Other Charges</label>
                  <input
                    type="number"
                    step="0.01"
                    value={formData.other_charges_paid}
                    onChange={(e) => setFormData({ ...formData, other_charges_paid: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Transaction Reference *</label>
                  <input
                    type="text"
                    value={formData.transaction_reference}
                    onChange={(e) => setFormData({ ...formData, transaction_reference: e.target.value })}
                    required
                    placeholder="Ref/Cheque/UTR number"
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
                  {loading ? 'Creating...' : 'Create Repayment'}
                </button>
              </div>
            </form>
          </div>
        )}

        {/* Filters */}
        <div className="bg-white rounded-lg shadow-sm p-6 mb-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Search Repayments</h2>
          <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
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
              <label className="block text-sm font-medium text-gray-700 mb-2">Payment Mode</label>
              <select
                value={paymentMode}
                onChange={(e) => setPaymentMode(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                <option value="">All Modes</option>
                <option value="cash">Cash</option>
                <option value="cheque">Cheque</option>
                <option value="neft">NEFT</option>
                <option value="imps">IMPS</option>
                <option value="rtgs">RTGS</option>
                <option value="upi">UPI</option>
                <option value="auto_debit">Auto Debit</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Status</label>
              <select
                value={transactionStatus}
                onChange={(e) => setTransactionStatus(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                <option value="">All Statuses</option>
                <option value="pending">Pending</option>
                <option value="completed">Completed</option>
                <option value="bounced">Bounced</option>
                <option value="reversed">Reversed</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">From Date</label>
              <input
                type="date"
                value={dateFrom}
                onChange={(e) => setDateFrom(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">To Date</label>
              <input
                type="date"
                value={dateTo}
                onChange={(e) => setDateTo(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
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

        {/* Repayments Table */}
        <div className="bg-white rounded-lg shadow-sm overflow-hidden">
          {loading ? (
            <div className="p-12 text-center">
              <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
              <p className="mt-4 text-gray-600">Loading repayments...</p>
            </div>
          ) : repayments.length === 0 ? (
            <div className="p-12 text-center">
              <div className="text-gray-400 text-5xl mb-4">💰</div>
              <p className="text-gray-600 text-lg">No repayments found</p>
              <p className="text-gray-500 text-sm mt-2">Record a new payment to get started</p>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Transaction
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Date
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Mode
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Amount Paid
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Principal
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Interest
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Penalty
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
                  {repayments.map((repayment) => (
                    <tr key={repayment.id} className="hover:bg-gray-50 transition-colors">
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm font-medium text-gray-900">{repayment.transaction_reference}</div>
                        <div className="text-xs text-gray-500">{repayment.loan_account_number || repayment.loan_account_id}</div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm text-gray-900">{formatDate(repayment.transaction_date)}</div>
                        {repayment.verified_at && (
                          <div className="text-xs text-green-600">
                            Verified: {formatDate(repayment.verified_at)}
                          </div>
                        )}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className={`px-2 py-1 text-xs font-medium rounded-full ${getPaymentModeBadge(repayment.payment_mode)}`}>
                          {repayment.payment_mode.toUpperCase()}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm font-medium text-gray-900">
                          {formatAmount(repayment.amount_paid)}
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600">
                        {formatAmount(repayment.principal_paid)}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600">
                        {formatAmount(repayment.interest_paid)}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600">
                        {formatAmount(repayment.penalty_paid)}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className={`px-2 py-1 text-xs font-medium rounded-full ${getStatusBadgeClass(repayment.transaction_status)}`}>
                          {repayment.transaction_status.toUpperCase()}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium space-x-2">
                        {repayment.transaction_status === 'pending' && (
                          <button
                            onClick={() => handleVerifyRepayment(repayment.id)}
                            className="text-green-600 hover:text-green-900"
                          >
                            Verify
                          </button>
                        )}
                        {repayment.transaction_status === 'completed' && (
                          <button
                            onClick={() => handleReverseRepayment(repayment.id)}
                            className="text-red-600 hover:text-red-900"
                          >
                            Reverse
                          </button>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>

        {/* Repayments Count */}
        {!loading && repayments.length > 0 && (
          <div className="mt-4 text-center text-sm text-gray-600">
            Showing {repayments.length} repayment transaction{repayments.length !== 1 ? 's' : ''}
          </div>
        )}
      </div>
    </div>
  );
}
