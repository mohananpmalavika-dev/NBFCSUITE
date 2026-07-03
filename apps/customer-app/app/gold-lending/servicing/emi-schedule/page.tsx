'use client';

import { useState, useEffect } from 'react';
import { goldApi } from '../../goldApi';
import Link from 'next/link';

interface EMISchedule {
  id: string;
  loan_account_id: string;
  loan_account_number?: string;
  emi_number: number;
  due_date: string;
  principal_amount: number;
  interest_amount: number;
  total_emi_amount: number;
  outstanding_principal: number;
  payment_status: string;
  paid_amount?: number;
  paid_date?: string;
  paid_principal?: number;
  paid_interest?: number;
  waived_amount?: number;
  penalty_amount?: number;
  overdue_days?: number;
}

interface EMISummary {
  total_emis: number;
  paid_emis: number;
  pending_emis: number;
  overdue_emis: number;
  total_emi_amount: number;
  total_paid: number;
  total_outstanding: number;
  next_emi_date?: string;
  next_emi_amount?: number;
}

export default function EMISchedulePage() {
  const [schedules, setSchedules] = useState<EMISchedule[]>([]);
  const [summary, setSummary] = useState<EMISummary | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  
  // Filters
  const [loanAccountId, setLoanAccountId] = useState('');
  const [paymentStatus, setPaymentStatus] = useState('');
  const [showOverdueOnly, setShowOverdueOnly] = useState(false);

  const loadEMISchedule = async () => {
    if (!loanAccountId) {
      setError('Please enter a loan account ID');
      return;
    }

    try {
      setLoading(true);
      setError('');
      
      let data: EMISchedule[];
      if (showOverdueOnly) {
        data = await goldApi.getOverdueEMIs(loanAccountId);
      } else {
        data = await goldApi.getEMISchedule(loanAccountId, paymentStatus || undefined);
      }
      
      setSchedules(data);
    } catch (err: any) {
      setError(err.message || 'Failed to load EMI schedule');
      setSchedules([]);
    } finally {
      setLoading(false);
    }
  };

  const loadSummary = async () => {
    if (!loanAccountId) return;

    try {
      const data = await goldApi.getEMISummary(loanAccountId);
      setSummary(data);
    } catch (err) {
      console.error('Failed to load EMI summary:', err);
    }
  };

  useEffect(() => {
    if (loanAccountId) {
      loadSummary();
    }
  }, [loanAccountId]);

  const handleGenerateSchedule = async () => {
    if (!loanAccountId) {
      setError('Please enter a loan account ID');
      return;
    }

    try {
      setLoading(true);
      setError('');
      await goldApi.generateEMISchedule(loanAccountId);
      await loadEMISchedule();
      await loadSummary();
    } catch (err: any) {
      setError(err.message || 'Failed to generate EMI schedule');
    } finally {
      setLoading(false);
    }
  };

  const getStatusBadgeClass = (status: string) => {
    const classes: Record<string, string> = {
      'pending': 'bg-yellow-100 text-yellow-800',
      'paid': 'bg-green-100 text-green-800',
      'partially_paid': 'bg-blue-100 text-blue-800',
      'overdue': 'bg-red-100 text-red-800',
      'waived': 'bg-gray-100 text-gray-800',
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

  const isOverdue = (dueDate: string, status: string) => {
    if (status === 'paid' || status === 'waived') return false;
    return new Date(dueDate) < new Date();
  };

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">EMI Schedule Management</h1>
              <p className="text-gray-600 mt-1">View and manage loan EMI schedules</p>
            </div>
            <Link
              href="/gold-lending/servicing/repayments"
              className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-medium"
            >
              Record Payment
            </Link>
          </div>

          {/* Summary Cards */}
          {summary && (
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
              <div className="bg-white rounded-lg shadow p-4">
                <div className="text-sm text-gray-600 mb-1">Total EMIs</div>
                <div className="text-2xl font-bold text-gray-900">{summary.total_emis}</div>
              </div>
              <div className="bg-green-50 rounded-lg shadow p-4">
                <div className="text-sm text-green-600 mb-1">Paid</div>
                <div className="text-2xl font-bold text-green-900">{summary.paid_emis}</div>
              </div>
              <div className="bg-yellow-50 rounded-lg shadow p-4">
                <div className="text-sm text-yellow-600 mb-1">Pending</div>
                <div className="text-2xl font-bold text-yellow-900">{summary.pending_emis}</div>
              </div>
              <div className="bg-red-50 rounded-lg shadow p-4">
                <div className="text-sm text-red-600 mb-1">Overdue</div>
                <div className="text-2xl font-bold text-red-900">{summary.overdue_emis}</div>
              </div>
            </div>
          )}

          {/* Amount Summary */}
          {summary && (
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
              <div className="bg-gradient-to-r from-blue-500 to-blue-600 rounded-lg shadow p-6 text-white">
                <div className="text-sm opacity-90 mb-2">Total EMI Amount</div>
                <div className="text-3xl font-bold">{formatAmount(summary.total_emi_amount)}</div>
              </div>
              <div className="bg-gradient-to-r from-green-500 to-green-600 rounded-lg shadow p-6 text-white">
                <div className="text-sm opacity-90 mb-2">Total Paid</div>
                <div className="text-3xl font-bold">{formatAmount(summary.total_paid)}</div>
              </div>
              <div className="bg-gradient-to-r from-orange-500 to-orange-600 rounded-lg shadow p-6 text-white">
                <div className="text-sm opacity-90 mb-2">Total Outstanding</div>
                <div className="text-3xl font-bold">{formatAmount(summary.total_outstanding)}</div>
              </div>
            </div>
          )}

          {/* Next EMI Info */}
          {summary?.next_emi_date && (
            <div className="bg-gradient-to-r from-purple-500 to-purple-600 rounded-lg shadow p-6 text-white mb-6">
              <div className="flex items-center justify-between">
                <div>
                  <div className="text-sm opacity-90 mb-2">Next EMI Due</div>
                  <div className="text-2xl font-bold">{formatDate(summary.next_emi_date)}</div>
                </div>
                <div className="text-right">
                  <div className="text-sm opacity-90 mb-2">Amount Due</div>
                  <div className="text-2xl font-bold">{formatAmount(summary.next_emi_amount || 0)}</div>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Search & Filters */}
        <div className="bg-white rounded-lg shadow-sm p-6 mb-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Search EMI Schedule</h2>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className="md:col-span-2">
              <label className="block text-sm font-medium text-gray-700 mb-2">Loan Account ID *</label>
              <input
                type="text"
                value={loanAccountId}
                onChange={(e) => setLoanAccountId(e.target.value)}
                placeholder="Enter loan account ID"
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Payment Status</label>
              <select
                value={paymentStatus}
                onChange={(e) => setPaymentStatus(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                disabled={showOverdueOnly}
              >
                <option value="">All Statuses</option>
                <option value="pending">Pending</option>
                <option value="paid">Paid</option>
                <option value="partially_paid">Partially Paid</option>
                <option value="overdue">Overdue</option>
                <option value="waived">Waived</option>
              </select>
            </div>

            <div className="flex items-end">
              <label className="flex items-center space-x-2">
                <input
                  type="checkbox"
                  checked={showOverdueOnly}
                  onChange={(e) => setShowOverdueOnly(e.target.checked)}
                  className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                />
                <span className="text-sm font-medium text-gray-700">Show Overdue Only</span>
              </label>
            </div>
          </div>

          <div className="mt-4 flex justify-end gap-2">
            <button
              onClick={handleGenerateSchedule}
              className="px-4 py-2 text-green-700 bg-green-100 rounded-lg hover:bg-green-200 transition-colors"
            >
              Generate Schedule
            </button>
            <button
              onClick={loadEMISchedule}
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
            >
              Load Schedule
            </button>
          </div>
        </div>

        {/* Error Message */}
        {error && (
          <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg mb-6">
            {error}
          </div>
        )}

        {/* EMI Schedule Table */}
        <div className="bg-white rounded-lg shadow-sm overflow-hidden">
          {loading ? (
            <div className="p-12 text-center">
              <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
              <p className="mt-4 text-gray-600">Loading EMI schedule...</p>
            </div>
          ) : schedules.length === 0 ? (
            <div className="p-12 text-center">
              <div className="text-gray-400 text-5xl mb-4">📅</div>
              <p className="text-gray-600 text-lg">No EMI schedule found</p>
              <p className="text-gray-500 text-sm mt-2">Enter a loan account ID and click "Load Schedule"</p>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      EMI #
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Due Date
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Principal
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Interest
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Total EMI
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Paid Amount
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Outstanding
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Status
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Overdue
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {schedules.map((emi) => (
                    <tr 
                      key={emi.id} 
                      className={`hover:bg-gray-50 transition-colors ${
                        isOverdue(emi.due_date, emi.payment_status) ? 'bg-red-50' : ''
                      }`}
                    >
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm font-medium text-gray-900">EMI #{emi.emi_number}</div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm text-gray-900">{formatDate(emi.due_date)}</div>
                        {emi.paid_date && (
                          <div className="text-xs text-green-600">
                            Paid: {formatDate(emi.paid_date)}
                          </div>
                        )}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm text-gray-900">{formatAmount(emi.principal_amount)}</div>
                        {emi.paid_principal && (
                          <div className="text-xs text-green-600">
                            Paid: {formatAmount(emi.paid_principal)}
                          </div>
                        )}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm text-gray-900">{formatAmount(emi.interest_amount)}</div>
                        {emi.paid_interest && (
                          <div className="text-xs text-green-600">
                            Paid: {formatAmount(emi.paid_interest)}
                          </div>
                        )}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm font-medium text-gray-900">
                          {formatAmount(emi.total_emi_amount)}
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm text-green-600">
                          {formatAmount(emi.paid_amount || 0)}
                        </div>
                        {emi.waived_amount && emi.waived_amount > 0 && (
                          <div className="text-xs text-gray-500">
                            Waived: {formatAmount(emi.waived_amount)}
                          </div>
                        )}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm text-orange-600 font-medium">
                          {formatAmount(emi.outstanding_principal)}
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className={`px-2 py-1 text-xs font-medium rounded-full ${getStatusBadgeClass(emi.payment_status)}`}>
                          {emi.payment_status.replace('_', ' ').toUpperCase()}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        {emi.overdue_days && emi.overdue_days > 0 ? (
                          <div>
                            <div className="text-sm text-red-600 font-medium">
                              {emi.overdue_days} days
                            </div>
                            {emi.penalty_amount && emi.penalty_amount > 0 && (
                              <div className="text-xs text-red-500">
                                Penalty: {formatAmount(emi.penalty_amount)}
                              </div>
                            )}
                          </div>
                        ) : (
                          <span className="text-sm text-gray-400">-</span>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>

        {/* Schedule Count */}
        {!loading && schedules.length > 0 && (
          <div className="mt-4 text-center text-sm text-gray-600">
            Showing {schedules.length} EMI installment{schedules.length !== 1 ? 's' : ''}
          </div>
        )}
      </div>
    </div>
  );
}
