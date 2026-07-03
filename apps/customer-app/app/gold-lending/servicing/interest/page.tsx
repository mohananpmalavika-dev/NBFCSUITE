'use client';

import { useState, useEffect } from 'react';
import { goldApi } from '../../goldApi';

interface InterestAccrual {
  id: string;
  loan_account_id: string;
  loan_account_number?: string;
  accrual_date: string;
  principal_balance: number;
  interest_rate: number;
  days_in_period: number;
  interest_accrued: number;
  cumulative_interest: number;
  accrual_status: string;
  reversal_reason?: string;
  created_at: string;
}

interface AccrualSummary {
  total_accruals: number;
  total_interest_accrued: number;
  posted_count: number;
  draft_count: number;
  reversed_count: number;
  active_loans: number;
  average_rate: number;
}

export default function InterestAccrualPage() {
  const [accruals, setAccruals] = useState<InterestAccrual[]>([]);
  const [summary, setSummary] = useState<AccrualSummary | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  
  // Filters
  const [loanAccountId, setLoanAccountId] = useState('');
  const [dateFrom, setDateFrom] = useState('');
  const [dateTo, setDateTo] = useState('');

  // Bulk Accrual
  const [showBulkForm, setShowBulkForm] = useState(false);
  const [bulkLoanIds, setBulkLoanIds] = useState('');
  const [bulkAccrualDate, setBulkAccrualDate] = useState(new Date().toISOString().split('T')[0]);

  // New Accrual Form
  const [showForm, setShowForm] = useState(false);
  const [formData, setFormData] = useState({
    loan_account_id: '',
    accrual_date: new Date().toISOString().split('T')[0],
    principal_balance: '',
    interest_rate: '',
    days_in_period: '1',
    interest_accrued: '',
    cumulative_interest: '',
  });

  useEffect(() => {
    if (loanAccountId) {
      loadAccruals();
    }
  }, [loanAccountId, dateFrom, dateTo]);

  const loadAccruals = async () => {
    if (!loanAccountId) {
      setError('Please enter a loan account ID');
      return;
    }

    try {
      setLoading(true);
      setError('');
      const data = await goldApi.getInterestAccruals(
        loanAccountId,
        dateFrom || undefined,
        dateTo || undefined
      );
      setAccruals(data);
    } catch (err: any) {
      setError(err.message || 'Failed to load interest accruals');
      setAccruals([]);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateAccrual = async (e: React.FormEvent) => {
    e.preventDefault();
    
    try {
      setLoading(true);
      setError('');
      setSuccess('');

      const payload = {
        ...formData,
        principal_balance: parseFloat(formData.principal_balance),
        interest_rate: parseFloat(formData.interest_rate),
        days_in_period: parseInt(formData.days_in_period),
        interest_accrued: parseFloat(formData.interest_accrued),
        cumulative_interest: parseFloat(formData.cumulative_interest || '0'),
      };

      await goldApi.createInterestAccrual(payload);
      setSuccess('Interest accrual created successfully!');
      setShowForm(false);
      resetForm();
      loadAccruals();
    } catch (err: any) {
      setError(err.message || 'Failed to create interest accrual');
    } finally {
      setLoading(false);
    }
  };

  const handleBulkAccrual = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!bulkLoanIds.trim()) {
      setError('Please enter loan account IDs');
      return;
    }

    try {
      setLoading(true);
      setError('');
      setSuccess('');

      const loanIds = bulkLoanIds.split(',').map(id => id.trim()).filter(id => id);
      await goldApi.bulkInterestAccrual(loanIds, bulkAccrualDate);
      
      setSuccess(`Bulk interest accrual processed for ${loanIds.length} loan account(s)!`);
      setShowBulkForm(false);
      setBulkLoanIds('');
    } catch (err: any) {
      setError(err.message || 'Failed to process bulk accrual');
    } finally {
      setLoading(false);
    }
  };

  const resetForm = () => {
    setFormData({
      loan_account_id: loanAccountId || '',
      accrual_date: new Date().toISOString().split('T')[0],
      principal_balance: '',
      interest_rate: '',
      days_in_period: '1',
      interest_accrued: '',
      cumulative_interest: '',
    });
  };

  const calculateInterest = () => {
    const principal = parseFloat(formData.principal_balance);
    const rate = parseFloat(formData.interest_rate);
    const days = parseInt(formData.days_in_period);

    if (principal && rate && days) {
      const dailyRate = rate / 365 / 100;
      const interest = principal * dailyRate * days;
      setFormData({
        ...formData,
        interest_accrued: interest.toFixed(2),
      });
    }
  };

  const getStatusBadgeClass = (status: string) => {
    const classes: Record<string, string> = {
      'draft': 'bg-gray-100 text-gray-800',
      'posted': 'bg-green-100 text-green-800',
      'reversed': 'bg-red-100 text-red-800',
    };
    return classes[status] || 'bg-gray-100 text-gray-800';
  };

  const formatAmount = (amount: number) => {
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR',
      maximumFractionDigits: 2,
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
              <h1 className="text-3xl font-bold text-gray-900">Interest Accrual Management</h1>
              <p className="text-gray-600 mt-1">Daily interest accrual tracking and processing</p>
            </div>
            <div className="flex gap-2">
              <button
                onClick={() => setShowBulkForm(!showBulkForm)}
                className="px-6 py-3 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors font-medium"
              >
                Bulk Accrual
              </button>
              <button
                onClick={() => setShowForm(!showForm)}
                className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-medium"
              >
                {showForm ? 'Cancel' : '+ New Accrual'}
              </button>
            </div>
          </div>

          {/* Summary Info */}
          <div className="bg-gradient-to-r from-indigo-500 to-indigo-600 rounded-lg shadow p-6 text-white">
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              <div>
                <div className="text-sm opacity-90 mb-1">Today's Date</div>
                <div className="text-xl font-bold">{formatDate(new Date().toISOString())}</div>
              </div>
              <div>
                <div className="text-sm opacity-90 mb-1">Accrual Method</div>
                <div className="text-xl font-bold">Daily (365 Days)</div>
              </div>
              <div>
                <div className="text-sm opacity-90 mb-1">Calculation Basis</div>
                <div className="text-xl font-bold">Reducing Balance</div>
              </div>
              <div>
                <div className="text-sm opacity-90 mb-1">Status</div>
                <div className="text-xl font-bold">Active</div>
              </div>
            </div>
          </div>
        </div>

        {/* Bulk Accrual Form */}
        {showBulkForm && (
          <div className="bg-white rounded-lg shadow-sm p-6 mb-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Bulk Interest Accrual</h2>
            <form onSubmit={handleBulkAccrual}>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Loan Account IDs * (comma-separated)
                  </label>
                  <textarea
                    value={bulkLoanIds}
                    onChange={(e) => setBulkLoanIds(e.target.value)}
                    placeholder="LA001, LA002, LA003..."
                    rows={3}
                    required
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                  <p className="text-xs text-gray-500 mt-1">Enter multiple loan account IDs separated by commas</p>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Accrual Date *</label>
                  <input
                    type="date"
                    value={bulkAccrualDate}
                    onChange={(e) => setBulkAccrualDate(e.target.value)}
                    required
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                  <p className="text-xs text-gray-500 mt-1">Interest will be accrued for all specified accounts</p>
                </div>
              </div>

              <div className="flex justify-end gap-2">
                <button
                  type="button"
                  onClick={() => setShowBulkForm(false)}
                  className="px-4 py-2 text-gray-700 bg-gray-100 rounded-lg hover:bg-gray-200 transition-colors"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={loading}
                  className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors disabled:bg-gray-400"
                >
                  {loading ? 'Processing...' : 'Process Bulk Accrual'}
                </button>
              </div>
            </form>
          </div>
        )}

        {/* New Accrual Form */}
        {showForm && (
          <div className="bg-white rounded-lg shadow-sm p-6 mb-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Create Interest Accrual</h2>
            <form onSubmit={handleCreateAccrual}>
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
                  <label className="block text-sm font-medium text-gray-700 mb-2">Accrual Date *</label>
                  <input
                    type="date"
                    value={formData.accrual_date}
                    onChange={(e) => setFormData({ ...formData, accrual_date: e.target.value })}
                    required
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Days in Period *</label>
                  <input
                    type="number"
                    value={formData.days_in_period}
                    onChange={(e) => setFormData({ ...formData, days_in_period: e.target.value })}
                    required
                    min="1"
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Principal Balance *</label>
                  <input
                    type="number"
                    step="0.01"
                    value={formData.principal_balance}
                    onChange={(e) => setFormData({ ...formData, principal_balance: e.target.value })}
                    required
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Interest Rate (%) *</label>
                  <input
                    type="number"
                    step="0.01"
                    value={formData.interest_rate}
                    onChange={(e) => setFormData({ ...formData, interest_rate: e.target.value })}
                    required
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Interest Accrued *
                    <button
                      type="button"
                      onClick={calculateInterest}
                      className="ml-2 text-xs text-blue-600 hover:text-blue-800"
                    >
                      Calculate
                    </button>
                  </label>
                  <input
                    type="number"
                    step="0.01"
                    value={formData.interest_accrued}
                    onChange={(e) => setFormData({ ...formData, interest_accrued: e.target.value })}
                    required
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Cumulative Interest</label>
                  <input
                    type="number"
                    step="0.01"
                    value={formData.cumulative_interest}
                    onChange={(e) => setFormData({ ...formData, cumulative_interest: e.target.value })}
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
                  {loading ? 'Creating...' : 'Create Accrual'}
                </button>
              </div>
            </form>
          </div>
        )}

        {/* Search Filters */}
        <div className="bg-white rounded-lg shadow-sm p-6 mb-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Search Accruals</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
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

          <div className="mt-4 flex justify-end">
            <button
              onClick={loadAccruals}
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
            >
              Search Accruals
            </button>
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

        {/* Accruals Table */}
        <div className="bg-white rounded-lg shadow-sm overflow-hidden">
          {loading ? (
            <div className="p-12 text-center">
              <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
              <p className="mt-4 text-gray-600">Loading interest accruals...</p>
            </div>
          ) : accruals.length === 0 ? (
            <div className="p-12 text-center">
              <div className="text-gray-400 text-5xl mb-4">📊</div>
              <p className="text-gray-600 text-lg">No interest accruals found</p>
              <p className="text-gray-500 text-sm mt-2">Enter a loan account ID and search</p>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Accrual Date
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Principal Balance
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Interest Rate
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Days
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Interest Accrued
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Cumulative Interest
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Status
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Created
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {accruals.map((accrual) => (
                    <tr key={accrual.id} className="hover:bg-gray-50 transition-colors">
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm font-medium text-gray-900">{formatDate(accrual.accrual_date)}</div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        {formatAmount(accrual.principal_balance)}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        {accrual.interest_rate.toFixed(2)}%
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        {accrual.days_in_period}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-green-600">
                        {formatAmount(accrual.interest_accrued)}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-blue-600">
                        {formatAmount(accrual.cumulative_interest)}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className={`px-2 py-1 text-xs font-medium rounded-full ${getStatusBadgeClass(accrual.accrual_status)}`}>
                          {accrual.accrual_status.toUpperCase()}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {formatDate(accrual.created_at)}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>

        {/* Accruals Count */}
        {!loading && accruals.length > 0 && (
          <div className="mt-4 text-center text-sm text-gray-600">
            Showing {accruals.length} accrual record{accruals.length !== 1 ? 's' : ''}
            {accruals.length > 0 && (
              <span className="ml-4 font-medium text-green-600">
                Total Interest: {formatAmount(accruals.reduce((sum, a) => sum + a.interest_accrued, 0))}
              </span>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
