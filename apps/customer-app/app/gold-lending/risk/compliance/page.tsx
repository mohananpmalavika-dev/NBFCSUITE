'use client';

import { useEffect, useState } from 'react';
import { goldApi } from '../../goldApi';

export default function CompliancePage() {
  const [checks, setChecks] = useState<any[]>([]);
  const [statistics, setStatistics] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [filters, setFilters] = useState({ compliance_area: '', compliance_status: '', review_status: '' });

  useEffect(() => {
    loadData();
  }, [filters]);

  const loadData = async () => {
    try {
      setLoading(true);
      const [checksData, stats] = await Promise.all([
        goldApi.listComplianceChecks({
          compliance_area: filters.compliance_area || undefined,
          compliance_status: filters.compliance_status || undefined,
          review_status: filters.review_status || undefined,
          limit: 50
        }),
        goldApi.getComplianceStatistics()
      ]);
      setChecks(checksData);
      setStatistics(stats);
    } catch (err) {
      console.error('Failed to load data:', err);
    } finally {
      setLoading(false);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status?.toLowerCase()) {
      case 'compliant': return 'bg-green-100 text-green-800';
      case 'non_compliant': return 'bg-red-100 text-red-800';
      case 'partially_compliant': return 'bg-yellow-100 text-yellow-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getReviewColor = (status: string) => {
    switch (status?.toLowerCase()) {
      case 'approved': return 'bg-green-100 text-green-800';
      case 'reviewed': return 'bg-blue-100 text-blue-800';
      case 'pending': return 'bg-yellow-100 text-yellow-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  return (
    <div className="p-6 space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Compliance Monitoring</h1>
          <p className="text-gray-600 mt-1">Track regulatory compliance and audit requirements</p>
        </div>
        <button className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700">
          New Check
        </button>
      </div>

      {/* Statistics */}
      {statistics && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className="bg-white rounded-lg shadow p-4">
            <div className="text-sm text-gray-600">Total Checks</div>
            <div className="text-2xl font-bold text-gray-900 mt-2">{statistics.total_checks}</div>
          </div>
          <div className="bg-white rounded-lg shadow p-4">
            <div className="text-sm text-gray-600">Compliant</div>
            <div className="text-2xl font-bold text-green-600 mt-2">
              {statistics.checks_by_compliance_status?.compliant || 0}
            </div>
          </div>
          <div className="bg-white rounded-lg shadow p-4">
            <div className="text-sm text-gray-600">Non-Compliant</div>
            <div className="text-2xl font-bold text-red-600 mt-2">
              {statistics.checks_by_compliance_status?.non_compliant || 0}
            </div>
          </div>
          <div className="bg-white rounded-lg shadow p-4">
            <div className="text-sm text-gray-600">Pending Review</div>
            <div className="text-2xl font-bold text-yellow-600 mt-2">
              {statistics.checks_by_review_status?.pending || 0}
            </div>
          </div>
        </div>
      )}

      {/* Filters */}
      <div className="bg-white rounded-lg shadow p-4">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <select
            value={filters.compliance_area}
            onChange={(e) => setFilters({ ...filters, compliance_area: e.target.value })}
            className="px-3 py-2 border border-gray-300 rounded-lg"
          >
            <option value="">All Areas</option>
            <option value="aml">AML/KYC</option>
            <option value="data_privacy">Data Privacy</option>
            <option value="financial_reporting">Financial Reporting</option>
            <option value="lending">Lending Regulations</option>
          </select>
          <select
            value={filters.compliance_status}
            onChange={(e) => setFilters({ ...filters, compliance_status: e.target.value })}
            className="px-3 py-2 border border-gray-300 rounded-lg"
          >
            <option value="">All Status</option>
            <option value="compliant">Compliant</option>
            <option value="non_compliant">Non-Compliant</option>
            <option value="partially_compliant">Partially Compliant</option>
          </select>
          <select
            value={filters.review_status}
            onChange={(e) => setFilters({ ...filters, review_status: e.target.value })}
            className="px-3 py-2 border border-gray-300 rounded-lg"
          >
            <option value="">All Review Status</option>
            <option value="pending">Pending</option>
            <option value="reviewed">Reviewed</option>
            <option value="approved">Approved</option>
          </select>
          <button
            onClick={() => setFilters({ compliance_area: '', compliance_status: '', review_status: '' })}
            className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50"
          >
            Clear
          </button>
        </div>
      </div>

      {/* Checks Table */}
      <div className="bg-white rounded-lg shadow overflow-hidden">
        {loading ? (
          <div className="p-8 text-center"><div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div></div>
        ) : (
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Check #</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Type</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Area</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Compliance</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Review</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Date</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Actions</th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {checks.map((check) => (
                <tr key={check.check_id} className="hover:bg-gray-50">
                  <td className="px-6 py-4 text-sm font-medium">{check.check_number}</td>
                  <td className="px-6 py-4 text-sm">{check.check_type}</td>
                  <td className="px-6 py-4 text-sm">{check.compliance_area}</td>
                  <td className="px-6 py-4">
                    <span className={`px-2 py-1 text-xs font-medium rounded-full ${getStatusColor(check.compliance_status)}`}>
                      {check.compliance_status}
                    </span>
                  </td>
                  <td className="px-6 py-4">
                    <span className={`px-2 py-1 text-xs font-medium rounded-full ${getReviewColor(check.review_status)}`}>
                      {check.review_status}
                    </span>
                  </td>
                  <td className="px-6 py-4 text-sm">{new Date(check.check_date).toLocaleDateString()}</td>
                  <td className="px-6 py-4 text-sm">
                    <button className="text-blue-600 hover:text-blue-800">View</button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
}
