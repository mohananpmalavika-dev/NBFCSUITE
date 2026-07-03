'use client';

import { useState, useEffect } from 'react';
import { goldApi } from '../../goldApi';

interface LoanStatement {
  id: string;
  loan_account_id: string;
  loan_account_number?: string;
  statement_type: string;
  statement_period_start: string;
  statement_period_end: string;
  opening_principal: number;
  closing_principal: number;
  total_credits: number;
  total_debits: number;
  interest_charged: number;
  interest_paid: number;
  penalties_charged: number;
  statement_generated_at: string;
  statement_url?: string;
}

export default function StatementsPage() {
  const [statements, setStatements] = useState<LoanStatement[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  
  // Filters
  const [loanAccountId, setLoanAccountId] = useState('');
  const [statementType, setStatementType] = useState('');

  // New Statement Form
  const [showForm, setShowForm] = useState(false);
  const [formData, setFormData] = useState({
    loan_account_id: '',
    statement_type: 'monthly',
    statement_period_start: '',
    statement_period_end: '',
    opening_principal: '',
    closing_principal: '',
    total_credits: '',
    total_debits: '',
    interest_charged: '',
    interest_paid: '',
    penalties_charged: '',
  });

  // Bulk Generation
  const [showBulkForm, setShowBulkForm] = useState(false);
  const [bulkLoanIds, setBulkLoanIds] = useState('');
  const [bulkPeriodStart, setBulkPeriodStart] = useState('');
  const [bulkPeriodEnd, setBulkPeriodEnd] = useState('');
  const [bulkStatementType, setBulkStatementType] = useState('monthly');

  useEffect(() => {
    if (loanAccountId) {
      loadStatements();
    }
  }, [loanAccountId, statementType]);

  const loadStatements = async () => {
    if (!loanAccountId) {
      setError('Please enter a loan account ID');
      return;
    }

    try {
      setLoading(true);
      setError('');
      const data = await goldApi.getStatements(loanAccountId, statementType || undefined);
      setStatements(data);
    } catch (err: any) {
      setError(err.message || 'Failed to load statements');
      setStatements([]);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateStatement = async (e: React.FormEvent) => {
    e.preventDefault();
    
    try {
      setLoading(true);
      setError('');
      setSuccess('');

      const payload = {
        ...formData,
        opening_principal: parseFloat(formData.opening_principal),
        closing_principal: parseFloat(formData.closing_principal),
        total_credits: parseFloat(formData.total_credits || '0'),
        total_debits: parseFloat(formData.total_debits || '0'),
        interest_charged: parseFloat(formData.interest_charged || '0'),
        interest_paid: parseFloat(formData.interest_paid || '0'),
        penalties_charged: parseFloat(formData.penalties_charged || '0'),
      };

      await goldApi.createStatement(payload);
      setSuccess('Statement generated successfully!');
      setShowForm(false);
      resetForm();
      if (loanAccountId) loadStatements();
    } catch (err: any) {
      setError(err.message || 'Failed to generate statement');
    } finally {
      setLoading(false);
    }
  };

  const handleBulkGenerate = async (e: React.FormEvent) => {
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
      await goldApi.bulkGenerateStatements(loanIds, bulkPeriodStart, bulkPeriodEnd, bulkStatementType);
      
      setSuccess(`Bulk statements generated for ${loanIds.length} loan account(s)!`);
      setShowBulkForm(false);
      setBulkLoanIds('');
    } catch (err: any) {
      setError(err.message || 'Failed to generate bulk statements');
    } finally {
      setLoading(false);
    }
  };

  const resetForm = () => {
    setFormData({
      loan_account_id: loanAccountId || '',
      statement_type: 'monthly',
      statement_period_start: '',
      statement_period_end: '',
      opening_principal: '',
      closing_principal: '',
      total_credits: '',
      total_debits: '',
      interest_charged: '',
      interest_paid: '',
      penalties_charged: '',
    });
  };

  const getTypeBadgeClass = (type: string) => {
    const classes: Record<string, string> = {
      'monthly': 'bg-blue-100 text-blue-800',
      'quarterly': 'bg-green-100 text-green-800',
      'annual': 'bg-purple-100 text-purple-800',
      'on_demand': 'bg-orange-100 text-orange-800',
    };
    return classes[type] || 'bg-gray-100 text-gray-800';
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
              <h1 className="text-3xl font-bold text-gray-900">Loan Statements</h1>
              <p className="text-gray-600 mt-1">Generate and manage loan account statements</p>
            </div>
            <div className="flex gap-2">
              <button
                onClick={() => setShowBulkForm(!showBulkForm)}
                className="px-6 py-3 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors font-medium"
              >
                Bulk Generate
              </button>
              <button
                onClick={() => setShowForm(!showForm)}
                className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-medium"
              >
                {showForm ? 'Cancel' : '+ New Statement'}
              </button>
            </div>
          </div>

          {/* Info Cards */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
            <div className="bg-blue-50 rounded-lg shadow p-4">
              <div className="text-sm text-blue-600 mb-1">Monthly Statements</div>
              <div className="text-2xl font-bold text-blue-900">
                {statements.filter(s => s.statement_type === 'monthly').length}
              </div>
            </div>
            <div className="bg-green-50 rounded-lg shadow p-4">
              <div className="text-sm text-green-600 mb-1">Quarterly Statements</div>
              <div className="text-2xl font-bold text-green-900">
                {statements.filter(s => s.statement_type === 'quarterly').length}
              </div>
            </div>
            <div className="bg-purple-50 rounded-lg shadow p-4">
              <div className="text-sm text-purple-600 mb-1">Annual Statements</div>
              <div className="text-2xl font-bold text-purple-900">
                {statements.filter(s => s.statement_type === 'annual').length}
              </div>
            </div>
            <div className="bg-orange-50 rounded-lg shadow p-4">
              <div className="text-sm text-orange-600 mb-1">On-Demand</div>
              <div className="text-2xl font-bold text-orange-900">
                {statements.filter(s => s.statement_type === 'on_demand').length}
              </div>
            </div>
          </div>
        </div>

        {/* Bulk Generation Form */}
        {showBulkForm && (
          <div className="bg-white rounded-lg shadow-sm p-6 mb-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Bulk Statement Generation</h2>
            <form onSubmit={handleBulkGenerate}>
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
                </div>
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">Statement Type *</label>
                    <select
                      value={bulkStatementType}
                      onChange={(e) => setBulkStatementType(e.target.value)}
                      required
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    >
                      <option value="monthly">Monthly</option>
                      <option value="quarterly">Quarterly</option>
                      <option value="annual">Annual</option>
                      <option value="on_demand">On-Demand</option>
                    </select>
                  </div>
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Period Start *</label>
                  <input
                    type="date"
                    value={bulkPeriodStart}
                    onChange={(e) => setBulkPeriodStart(e.target.value)}
                    required
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Period End *</label>
                  <input
                    type="date"
                    value={bulkPeriodEnd}
                    onChange={(e) => setBulkPeriodEnd(e.target.value)}
                    required
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
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
                  {loading ? 'Generating...' : 'Generate Bulk Statements'}
                </button>
              </div>
            </form>
          </div>
        )}

        {/* New Statement Form */}
        {showForm && (
          <div className="bg-white rounded-lg shadow-sm p-6 mb-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Generate New Statement</h2>
            <form onSubmit={handleCreateStatement}>
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
                  <label className="block text-sm font-medium text-gray-700 mb-2">Statement Type *</label>
                  <select
                    value={formData.statement_type}
                    onChange={(e) => setFormData({ ...formData, statement_type: e.target.value })}
                    required
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  >
                    <option value="monthly">Monthly</option>
                    <option value="quarterly">Quarterly</option>
                    <option value="annual">Annual</option>
                    <option value="on_demand">On-Demand</option>
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Period Start *</label>
                  <input
                    type="date"
                    value={formData.statement_period_start}
                    onChange={(e) => setFormData({ ...formData, statement_period_start: e.target.value })}
                    required
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Period End *</label>
                  <input
                    type="date"
                    value={formData.statement_period_end}
                    onChange={(e) => setFormData({ ...formData, statement_period_end: e.target.value })}
                    required
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Opening Principal *</label>
                  <input
                    type="number"
                    step="0.01"
                    value={formData.opening_principal}
                    onChange={(e) => setFormData({ ...formData, opening_principal: e.target.value })}
                    required
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Closing Principal *</label>
                  <input
                    type="number"
                    step="0.01"
                    value={formData.closing_principal}
                    onChange={(e) => setFormData({ ...formData, closing_principal: e.target.value })}
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
                  {loading ? 'Generating...' : 'Generate Statement'}
                </button>
              </div>
            </form>
          </div>
        )}

        {/* Search Filters */}
        <div className="bg-white rounded-lg shadow-sm p-6 mb-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Search Statements</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
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
              <label className="block text-sm font-medium text-gray-700 mb-2">Statement Type</label>
              <select
                value={statementType}
                onChange={(e) => setStatementType(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                <option value="">All Types</option>
                <option value="monthly">Monthly</option>
                <option value="quarterly">Quarterly</option>
                <option value="annual">Annual</option>
                <option value="on_demand">On-Demand</option>
              </select>
            </div>
          </div>

          <div className="mt-4 flex justify-end">
            <button
              onClick={loadStatements}
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
            >
              Search Statements
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

        {/* Statements Table */}
        <div className="bg-white rounded-lg shadow-sm overflow-hidden">
          {loading ? (
            <div className="p-12 text-center">
              <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
              <p className="mt-4 text-gray-600">Loading statements...</p>
            </div>
          ) : statements.length === 0 ? (
            <div className="p-12 text-center">
              <div className="text-gray-400 text-5xl mb-4">📄</div>
              <p className="text-gray-600 text-lg">No statements found</p>
              <p className="text-gray-500 text-sm mt-2">Enter a loan account ID and search</p>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Statement Period
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Type
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Opening Principal
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Closing Principal
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Credits
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Debits
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Interest
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Generated
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Actions
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {statements.map((stmt) => (
                    <tr key={stmt.id} className="hover:bg-gray-50 transition-colors">
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm font-medium text-gray-900">
                          {formatDate(stmt.statement_period_start)}
                        </div>
                        <div className="text-xs text-gray-500">
                          to {formatDate(stmt.statement_period_end)}
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className={`px-2 py-1 text-xs font-medium rounded-full ${getTypeBadgeClass(stmt.statement_type)}`}>
                          {stmt.statement_type.replace('_', ' ').toUpperCase()}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        {formatAmount(stmt.opening_principal)}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                        {formatAmount(stmt.closing_principal)}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-green-600">
                        {formatAmount(stmt.total_credits)}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-red-600">
                        {formatAmount(stmt.total_debits)}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm text-gray-900">
                          Charged: {formatAmount(stmt.interest_charged)}
                        </div>
                        <div className="text-xs text-green-600">
                          Paid: {formatAmount(stmt.interest_paid)}
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {formatDate(stmt.statement_generated_at)}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                        {stmt.statement_url ? (
                          <a
                            href={stmt.statement_url}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="text-blue-600 hover:text-blue-900"
                          >
                            Download
                          </a>
                        ) : (
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

        {/* Statements Count */}
        {!loading && statements.length > 0 && (
          <div className="mt-4 text-center text-sm text-gray-600">
            Showing {statements.length} statement{statements.length !== 1 ? 's' : ''}
          </div>
        )}
      </div>
    </div>
  );
}
