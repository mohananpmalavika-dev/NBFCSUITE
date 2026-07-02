'use client';

import { useState, useEffect } from 'react';
import { goldApi } from '../goldApi';
import Link from 'next/link';

interface LoanApplication {
  id: string;
  application_number: string;
  customer_id: string;
  customer_name?: string;
  product_id: string;
  product_code?: string;
  branch_id: string;
  branch_name?: string;
  requested_amount: number;
  eligible_amount?: number;
  sanctioned_amount?: number;
  status: string;
  stage: string;
  created_at: string;
  submitted_at?: string;
  total_ornaments?: number;
  total_gold_weight?: number;
}

interface ApplicationSummary {
  total_applications: number;
  draft_count: number;
  pending_count: number;
  approved_count: number;
  rejected_count: number;
  disbursed_count: number;
  total_requested: number;
  total_sanctioned: number;
}

export default function LoansPage() {
  const [applications, setApplications] = useState<LoanApplication[]>([]);
  const [summary, setSummary] = useState<ApplicationSummary | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  
  // Filters
  const [statusFilter, setStatusFilter] = useState('');
  const [stageFilter, setStageFilter] = useState('');
  const [branchFilter, setBranchFilter] = useState('');
  const [dateFrom, setDateFrom] = useState('');
  const [dateTo, setDateTo] = useState('');

  useEffect(() => {
    loadApplications();
    loadSummary();
  }, [statusFilter, stageFilter, branchFilter, dateFrom, dateTo]);

  const loadApplications = async () => {
    try {
      setLoading(true);
      const filters: any = {};
      if (statusFilter) filters.status = statusFilter;
      if (stageFilter) filters.stage = stageFilter;
      if (branchFilter) filters.branch_id = branchFilter;
      if (dateFrom) filters.from_date = dateFrom;
      if (dateTo) filters.to_date = dateTo;
      
      const data = await goldApi.getLoanApplications(filters);
      setApplications(data);
      setError('');
    } catch (err: any) {
      setError(err.message || 'Failed to load applications');
    } finally {
      setLoading(false);
    }
  };

  const loadSummary = async () => {
    try {
      const filters: any = {};
      if (branchFilter) filters.branch_id = branchFilter;
      if (dateFrom) filters.from_date = dateFrom;
      if (dateTo) filters.to_date = dateTo;
      
      const data = await goldApi.getApplicationsSummary(filters);
      setSummary(data);
    } catch (err) {
      console.error('Failed to load summary:', err);
    }
  };

  const getStatusBadgeClass = (status: string) => {
    const classes: Record<string, string> = {
      'draft': 'bg-gray-100 text-gray-800',
      'submitted': 'bg-blue-100 text-blue-800',
      'under_review': 'bg-yellow-100 text-yellow-800',
      'approved': 'bg-green-100 text-green-800',
      'rejected': 'bg-red-100 text-red-800',
      'disbursed': 'bg-purple-100 text-purple-800',
      'cancelled': 'bg-gray-100 text-gray-800',
    };
    return classes[status] || 'bg-gray-100 text-gray-800';
  };

  const getStageBadgeClass = (stage: string) => {
    const classes: Record<string, string> = {
      'application': 'bg-blue-50 text-blue-700',
      'credit_evaluation': 'bg-yellow-50 text-yellow-700',
      'approval': 'bg-orange-50 text-orange-700',
      'documentation': 'bg-indigo-50 text-indigo-700',
      'disbursement': 'bg-green-50 text-green-700',
      'completed': 'bg-gray-50 text-gray-700',
    };
    return classes[stage] || 'bg-gray-50 text-gray-700';
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
              <h1 className="text-3xl font-bold text-gray-900">Loan Applications</h1>
              <p className="text-gray-600 mt-1">Manage gold loan applications and disbursements</p>
            </div>
            <Link
              href="/gold-lending/loans/new"
              className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-medium"
            >
              + New Application
            </Link>
          </div>

          {/* Summary Cards */}
          {summary && (
            <div className="grid grid-cols-1 md:grid-cols-4 lg:grid-cols-6 gap-4 mb-6">
              <div className="bg-white rounded-lg shadow p-4">
                <div className="text-sm text-gray-600 mb-1">Total</div>
                <div className="text-2xl font-bold text-gray-900">{summary.total_applications}</div>
              </div>
              <div className="bg-blue-50 rounded-lg shadow p-4">
                <div className="text-sm text-blue-600 mb-1">Pending</div>
                <div className="text-2xl font-bold text-blue-900">{summary.pending_count}</div>
              </div>
              <div className="bg-green-50 rounded-lg shadow p-4">
                <div className="text-sm text-green-600 mb-1">Approved</div>
                <div className="text-2xl font-bold text-green-900">{summary.approved_count}</div>
              </div>
              <div className="bg-red-50 rounded-lg shadow p-4">
                <div className="text-sm text-red-600 mb-1">Rejected</div>
                <div className="text-2xl font-bold text-red-900">{summary.rejected_count}</div>
              </div>
              <div className="bg-purple-50 rounded-lg shadow p-4">
                <div className="text-sm text-purple-600 mb-1">Disbursed</div>
                <div className="text-2xl font-bold text-purple-900">{summary.disbursed_count}</div>
              </div>
              <div className="bg-gray-50 rounded-lg shadow p-4">
                <div className="text-sm text-gray-600 mb-1">Draft</div>
                <div className="text-2xl font-bold text-gray-900">{summary.draft_count}</div>
              </div>
            </div>
          )}

          {/* Amount Summary */}
          {summary && (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
              <div className="bg-gradient-to-r from-blue-500 to-blue-600 rounded-lg shadow p-6 text-white">
                <div className="text-sm opacity-90 mb-2">Total Requested Amount</div>
                <div className="text-3xl font-bold">{formatAmount(summary.total_requested)}</div>
              </div>
              <div className="bg-gradient-to-r from-green-500 to-green-600 rounded-lg shadow p-6 text-white">
                <div className="text-sm opacity-90 mb-2">Total Sanctioned Amount</div>
                <div className="text-3xl font-bold">{formatAmount(summary.total_sanctioned)}</div>
              </div>
            </div>
          )}
        </div>

        {/* Filters */}
        <div className="bg-white rounded-lg shadow-sm p-6 mb-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Filters</h2>
          <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Status</label>
              <select
                value={statusFilter}
                onChange={(e) => setStatusFilter(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                <option value="">All Statuses</option>
                <option value="draft">Draft</option>
                <option value="submitted">Submitted</option>
                <option value="under_review">Under Review</option>
                <option value="approved">Approved</option>
                <option value="rejected">Rejected</option>
                <option value="disbursed">Disbursed</option>
                <option value="cancelled">Cancelled</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Stage</label>
              <select
                value={stageFilter}
                onChange={(e) => setStageFilter(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                <option value="">All Stages</option>
                <option value="application">Application</option>
                <option value="credit_evaluation">Credit Evaluation</option>
                <option value="approval">Approval</option>
                <option value="documentation">Documentation</option>
                <option value="disbursement">Disbursement</option>
                <option value="completed">Completed</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Branch ID</label>
              <input
                type="text"
                value={branchFilter}
                onChange={(e) => setBranchFilter(e.target.value)}
                placeholder="Enter branch ID"
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

          <div className="mt-4 flex justify-end gap-2">
            <button
              onClick={() => {
                setStatusFilter('');
                setStageFilter('');
                setBranchFilter('');
                setDateFrom('');
                setDateTo('');
              }}
              className="px-4 py-2 text-gray-700 bg-gray-100 rounded-lg hover:bg-gray-200 transition-colors"
            >
              Clear Filters
            </button>
            <button
              onClick={loadApplications}
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
            >
              Apply Filters
            </button>
          </div>
        </div>

        {/* Error Message */}
        {error && (
          <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg mb-6">
            {error}
          </div>
        )}

        {/* Applications Table */}
        <div className="bg-white rounded-lg shadow-sm overflow-hidden">
          {loading ? (
            <div className="p-12 text-center">
              <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
              <p className="mt-4 text-gray-600">Loading applications...</p>
            </div>
          ) : applications.length === 0 ? (
            <div className="p-12 text-center">
              <div className="text-gray-400 text-5xl mb-4">📋</div>
              <p className="text-gray-600 text-lg">No loan applications found</p>
              <p className="text-gray-500 text-sm mt-2">Create a new application to get started</p>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Application
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Customer
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Product
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Amounts
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Ornaments
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Status
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Stage
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Date
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Actions
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {applications.map((app) => (
                    <tr key={app.id} className="hover:bg-gray-50 transition-colors">
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm font-medium text-gray-900">{app.application_number}</div>
                        <div className="text-xs text-gray-500">{app.branch_name || app.branch_id}</div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm text-gray-900">{app.customer_name || app.customer_id}</div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm text-gray-900">{app.product_code || app.product_id}</div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm text-gray-900">
                          Req: {formatAmount(app.requested_amount)}
                        </div>
                        {app.sanctioned_amount && (
                          <div className="text-xs text-green-600">
                            San: {formatAmount(app.sanctioned_amount)}
                          </div>
                        )}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm text-gray-900">
                          {app.total_ornaments || 0} items
                        </div>
                        {app.total_gold_weight && (
                          <div className="text-xs text-gray-500">
                            {app.total_gold_weight.toFixed(2)}g
                          </div>
                        )}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className={`px-2 py-1 text-xs font-medium rounded-full ${getStatusBadgeClass(app.status)}`}>
                          {app.status.replace('_', ' ').toUpperCase()}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className={`px-2 py-1 text-xs font-medium rounded-full ${getStageBadgeClass(app.stage)}`}>
                          {app.stage.replace('_', ' ').toUpperCase()}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {formatDate(app.created_at)}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                        <Link
                          href={`/gold-lending/loans/${app.id}`}
                          className="text-blue-600 hover:text-blue-900"
                        >
                          View →
                        </Link>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>

        {/* Applications Count */}
        {!loading && applications.length > 0 && (
          <div className="mt-4 text-center text-sm text-gray-600">
            Showing {applications.length} application{applications.length !== 1 ? 's' : ''}
          </div>
        )}
      </div>
    </div>
  );
}
