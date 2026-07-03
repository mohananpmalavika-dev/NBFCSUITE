'use client';

import { useState, useEffect } from 'react';
import { goldApi } from '../../goldApi';

interface AutoDebitMandate {
  id: string;
  loan_account_id: string;
  loan_account_number?: string;
  mandate_type: string;
  bank_account_number: string;
  bank_name: string;
  ifsc_code: string;
  account_holder_name: string;
  mandate_amount: number;
  mandate_frequency: string;
  mandate_start_date: string;
  mandate_end_date: string;
  mandate_status: string;
  mandate_reference: string;
  created_at: string;
  activated_at?: string;
}

export default function MandatesPage() {
  const [mandates, setMandates] = useState<AutoDebitMandate[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  
  // Filters
  const [loanAccountId, setLoanAccountId] = useState('');
  const [mandateStatus, setMandateStatus] = useState('');

  // New Mandate Form
  const [showForm, setShowForm] = useState(false);
  const [formData, setFormData] = useState({
    loan_account_id: '',
    mandate_type: 'nach',
    bank_account_number: '',
    bank_name: '',
    ifsc_code: '',
    account_holder_name: '',
    mandate_amount: '',
    mandate_frequency: 'monthly',
    mandate_start_date: new Date().toISOString().split('T')[0],
    mandate_end_date: '',
    mandate_reference: '',
  });

  useEffect(() => {
    loadMandates();
  }, [loanAccountId, mandateStatus]);

  const loadMandates = async () => {
    try {
      setLoading(true);
      const filters: any = {};
      if (loanAccountId) filters.loan_account_id = loanAccountId;
      if (mandateStatus) filters.mandate_status = mandateStatus;
      
      const data = await goldApi.getMandates(filters);
      setMandates(data);
      setError('');
    } catch (err: any) {
      setError(err.message || 'Failed to load mandates');
      setMandates([]);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateMandate = async (e: React.FormEvent) => {
    e.preventDefault();
    
    try {
      setLoading(true);
      setError('');
      setSuccess('');

      const payload = {
        ...formData,
        mandate_amount: parseFloat(formData.mandate_amount),
      };

      await goldApi.createMandate(payload);
      setSuccess('Auto-debit mandate created successfully!');
      setShowForm(false);
      resetForm();
      loadMandates();
    } catch (err: any) {
      setError(err.message || 'Failed to create mandate');
    } finally {
      setLoading(false);
    }
  };

  const resetForm = () => {
    setFormData({
      loan_account_id: '',
      mandate_type: 'nach',
      bank_account_number: '',
      bank_name: '',
      ifsc_code: '',
      account_holder_name: '',
      mandate_amount: '',
      mandate_frequency: 'monthly',
      mandate_start_date: new Date().toISOString().split('T')[0],
      mandate_end_date: '',
      mandate_reference: '',
    });
  };

  const getTypeBadgeClass = (type: string) => {
    const classes: Record<string, string> = {
      'nach': 'bg-blue-100 text-blue-800',
      'emandate': 'bg-green-100 text-green-800',
      'standing_instruction': 'bg-purple-100 text-purple-800',
    };
    return classes[type] || 'bg-gray-100 text-gray-800';
  };

  const getStatusBadgeClass = (status: string) => {
    const classes: Record<string, string> = {
      'pending': 'bg-yellow-100 text-yellow-800',
      'active': 'bg-green-100 text-green-800',
      'expired': 'bg-gray-100 text-gray-800',
      'cancelled': 'bg-red-100 text-red-800',
      'suspended': 'bg-orange-100 text-orange-800',
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
              <h1 className="text-3xl font-bold text-gray-900">Auto-Debit Mandates</h1>
              <p className="text-gray-600 mt-1">Manage NACH, e-Mandate, and standing instructions</p>
            </div>
            <button
              onClick={() => setShowForm(!showForm)}
              className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-medium"
            >
              {showForm ? 'Cancel' : '+ New Mandate'}
            </button>
          </div>

          {/* Summary Cards */}
          <div className="grid grid-cols-1 md:grid-cols-5 gap-4 mb-6">
            <div className="bg-white rounded-lg shadow p-4">
              <div className="text-sm text-gray-600 mb-1">Total Mandates</div>
              <div className="text-2xl font-bold text-gray-900">{mandates.length}</div>
            </div>
            <div className="bg-green-50 rounded-lg shadow p-4">
              <div className="text-sm text-green-600 mb-1">Active</div>
              <div className="text-2xl font-bold text-green-900">
                {mandates.filter(m => m.mandate_status === 'active').length}
              </div>
            </div>
            <div className="bg-yellow-50 rounded-lg shadow p-4">
              <div className="text-sm text-yellow-600 mb-1">Pending</div>
              <div className="text-2xl font-bold text-yellow-900">
                {mandates.filter(m => m.mandate_status === 'pending').length}
              </div>
            </div>
            <div className="bg-gray-50 rounded-lg shadow p-4">
              <div className="text-sm text-gray-600 mb-1">Expired</div>
              <div className="text-2xl font-bold text-gray-900">
                {mandates.filter(m => m.mandate_status === 'expired').length}
              </div>
            </div>
            <div className="bg-red-50 rounded-lg shadow p-4">
              <div className="text-sm text-red-600 mb-1">Cancelled</div>
              <div className="text-2xl font-bold text-red-900">
                {mandates.filter(m => m.mandate_status === 'cancelled').length}
              </div>
            </div>
          </div>
        </div>

        {/* New Mandate Form */}
        {showForm && (
          <div className="bg-white rounded-lg shadow-sm p-6 mb-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Setup Auto-Debit Mandate</h2>
            <form onSubmit={handleCreateMandate}>
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
                  <label className="block text-sm font-medium text-gray-700 mb-2">Mandate Type *</label>
                  <select
                    value={formData.mandate_type}
                    onChange={(e) => setFormData({ ...formData, mandate_type: e.target.value })}
                    required
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  >
                    <option value="nach">NACH</option>
                    <option value="emandate">E-Mandate</option>
                    <option value="standing_instruction">Standing Instruction</option>
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Mandate Amount *</label>
                  <input
                    type="number"
                    step="0.01"
                    value={formData.mandate_amount}
                    onChange={(e) => setFormData({ ...formData, mandate_amount: e.target.value })}
                    required
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Bank Account Number *</label>
                  <input
                    type="text"
                    value={formData.bank_account_number}
                    onChange={(e) => setFormData({ ...formData, bank_account_number: e.target.value })}
                    required
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Bank Name *</label>
                  <input
                    type="text"
                    value={formData.bank_name}
                    onChange={(e) => setFormData({ ...formData, bank_name: e.target.value })}
                    required
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">IFSC Code *</label>
                  <input
                    type="text"
                    value={formData.ifsc_code}
                    onChange={(e) => setFormData({ ...formData, ifsc_code: e.target.value })}
                    required
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Account Holder Name *</label>
                  <input
                    type="text"
                    value={formData.account_holder_name}
                    onChange={(e) => setFormData({ ...formData, account_holder_name: e.target.value })}
                    required
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Frequency *</label>
                  <select
                    value={formData.mandate_frequency}
                    onChange={(e) => setFormData({ ...formData, mandate_frequency: e.target.value })}
                    required
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  >
                    <option value="monthly">Monthly</option>
                    <option value="quarterly">Quarterly</option>
                    <option value="weekly">Weekly</option>
                    <option value="as_needed">As Needed</option>
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Mandate Reference</label>
                  <input
                    type="text"
                    value={formData.mandate_reference}
                    onChange={(e) => setFormData({ ...formData, mandate_reference: e.target.value })}
                    placeholder="Optional reference"
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Start Date *</label>
                  <input
                    type="date"
                    value={formData.mandate_start_date}
                    onChange={(e) => setFormData({ ...formData, mandate_start_date: e.target.value })}
                    required
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">End Date *</label>
                  <input
                    type="date"
                    value={formData.mandate_end_date}
                    onChange={(e) => setFormData({ ...formData, mandate_end_date: e.target.value })}
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
                  {loading ? 'Creating...' : 'Create Mandate'}
                </button>
              </div>
            </form>
          </div>
        )}

        {/* Filters */}
        <div className="bg-white rounded-lg shadow-sm p-6 mb-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Filter Mandates</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
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
              <label className="block text-sm font-medium text-gray-700 mb-2">Mandate Status</label>
              <select
                value={mandateStatus}
                onChange={(e) => setMandateStatus(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                <option value="">All Statuses</option>
                <option value="pending">Pending</option>
                <option value="active">Active</option>
                <option value="expired">Expired</option>
                <option value="cancelled">Cancelled</option>
                <option value="suspended">Suspended</option>
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

        {/* Mandates Table */}
        <div className="bg-white rounded-lg shadow-sm overflow-hidden">
          {loading ? (
            <div className="p-12 text-center">
              <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
              <p className="mt-4 text-gray-600">Loading mandates...</p>
            </div>
          ) : mandates.length === 0 ? (
            <div className="p-12 text-center">
              <div className="text-gray-400 text-5xl mb-4">🏦</div>
              <p className="text-gray-600 text-lg">No mandates found</p>
              <p className="text-gray-500 text-sm mt-2">Create a new mandate to get started</p>
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
                      Type
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Bank Details
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Amount
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Frequency
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Validity Period
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Status
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Reference
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {mandates.map((mandate) => (
                    <tr key={mandate.id} className="hover:bg-gray-50 transition-colors">
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm font-medium text-gray-900">
                          {mandate.loan_account_number || mandate.loan_account_id}
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className={`px-2 py-1 text-xs font-medium rounded-full ${getTypeBadgeClass(mandate.mandate_type)}`}>
                          {mandate.mandate_type.replace('_', ' ').toUpperCase()}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm text-gray-900">{mandate.bank_name}</div>
                        <div className="text-xs text-gray-500">{mandate.account_holder_name}</div>
                        <div className="text-xs text-gray-500">A/C: {mandate.bank_account_number}</div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                        {formatAmount(mandate.mandate_amount)}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm text-gray-900 capitalize">
                          {mandate.mandate_frequency}
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm text-gray-900">{formatDate(mandate.mandate_start_date)}</div>
                        <div className="text-xs text-gray-500">to {formatDate(mandate.mandate_end_date)}</div>
                        {mandate.activated_at && (
                          <div className="text-xs text-green-600">
                            Activated: {formatDate(mandate.activated_at)}
                          </div>
                        )}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className={`px-2 py-1 text-xs font-medium rounded-full ${getStatusBadgeClass(mandate.mandate_status)}`}>
                          {mandate.mandate_status.toUpperCase()}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {mandate.mandate_reference || '-'}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>

        {/* Mandates Count */}
        {!loading && mandates.length > 0 && (
          <div className="mt-4 text-center text-sm text-gray-600">
            Showing {mandates.length} mandate{mandates.length !== 1 ? 's' : ''}
          </div>
        )}
      </div>
    </div>
  );
}
