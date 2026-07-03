'use client';

import { useState, useEffect } from 'react';
import { goldApi } from '../../goldApi';

export default function CollectionCasesPage() {
  const [cases, setCases] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [filters, setFilters] = useState({
    case_status: '',
    bucket_type: '',
    priority: '',
    skip: 0,
    limit: 50
  });
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [selectedCase, setSelectedCase] = useState<any>(null);

  useEffect(() => {
    fetchCases();
  }, [filters]);

  const fetchCases = async () => {
    try {
      setLoading(true);
      const response = await goldApi.getCollectionCases(filters);
      setCases(response.items || []);
    } catch (error) {
      console.error('Failed to fetch collection cases:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleStatusChange = (caseId: string, newStatus: string) => {
    goldApi.updateCollectionCase(caseId, { case_status: newStatus })
      .then(() => fetchCases())
      .catch(error => console.error('Failed to update case:', error));
  };

  const getBucketColor = (bucket: string) => {
    const colors: Record<string, string> = {
      'dpd_0_30': 'bg-yellow-100 text-yellow-800',
      'dpd_31_60': 'bg-orange-100 text-orange-800',
      'dpd_61_90': 'bg-red-100 text-red-800',
      'dpd_90_plus': 'bg-purple-100 text-purple-800',
      'npa': 'bg-gray-900 text-white'
    };
    return colors[bucket] || 'bg-gray-100 text-gray-800';
  };

  const getPriorityColor = (priority: string) => {
    const colors: Record<string, string> = {
      'low': 'bg-blue-100 text-blue-800',
      'medium': 'bg-green-100 text-green-800',
      'high': 'bg-orange-100 text-orange-800',
      'critical': 'bg-red-100 text-red-800'
    };
    return colors[priority] || 'bg-gray-100 text-gray-800';
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-lg">Loading collection cases...</div>
      </div>
    );
  }

  return (
    <div className="p-6 max-w-7xl mx-auto">
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-gray-900">Collection Cases</h1>
        <p className="text-gray-600 mt-2">Manage overdue loans and collection activities</p>
      </div>

      {/* Filters */}
      <div className="bg-white p-4 rounded-lg shadow mb-6">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Status</label>
            <select
              value={filters.case_status}
              onChange={(e) => setFilters({ ...filters, case_status: e.target.value })}
              className="w-full border border-gray-300 rounded-md px-3 py-2"
            >
              <option value="">All Statuses</option>
              <option value="open">Open</option>
              <option value="in_progress">In Progress</option>
              <option value="legal">Legal</option>
              <option value="npa">NPA</option>
              <option value="closed">Closed</option>
              <option value="settled">Settled</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Bucket</label>
            <select
              value={filters.bucket_type}
              onChange={(e) => setFilters({ ...filters, bucket_type: e.target.value })}
              className="w-full border border-gray-300 rounded-md px-3 py-2"
            >
              <option value="">All Buckets</option>
              <option value="dpd_0_30">0-30 Days</option>
              <option value="dpd_31_60">31-60 Days</option>
              <option value="dpd_61_90">61-90 Days</option>
              <option value="dpd_90_plus">90+ Days</option>
              <option value="npa">NPA</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Priority</label>
            <select
              value={filters.priority}
              onChange={(e) => setFilters({ ...filters, priority: e.target.value })}
              className="w-full border border-gray-300 rounded-md px-3 py-2"
            >
              <option value="">All Priorities</option>
              <option value="low">Low</option>
              <option value="medium">Medium</option>
              <option value="high">High</option>
              <option value="critical">Critical</option>
            </select>
          </div>

          <div className="flex items-end">
            <button
              onClick={() => setFilters({ case_status: '', bucket_type: '', priority: '', skip: 0, limit: 50 })}
              className="w-full bg-gray-200 text-gray-800 px-4 py-2 rounded-md hover:bg-gray-300"
            >
              Clear Filters
            </button>
          </div>
        </div>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-5 gap-4 mb-6">
        {[
          { label: 'Total Cases', value: cases.length, color: 'blue' },
          { label: 'DPD 0-30', value: cases.filter(c => c.bucket_type === 'dpd_0_30').length, color: 'yellow' },
          { label: 'DPD 31-60', value: cases.filter(c => c.bucket_type === 'dpd_31_60').length, color: 'orange' },
          { label: 'DPD 61-90', value: cases.filter(c => c.bucket_type === 'dpd_61_90').length, color: 'red' },
          { label: 'NPA', value: cases.filter(c => c.bucket_type === 'npa').length, color: 'purple' },
        ].map((stat) => (
          <div key={stat.label} className="bg-white p-4 rounded-lg shadow">
            <div className="text-sm text-gray-600">{stat.label}</div>
            <div className="text-2xl font-bold text-gray-900 mt-1">{stat.value}</div>
          </div>
        ))}
      </div>

      {/* Cases Table */}
      <div className="bg-white rounded-lg shadow overflow-hidden">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Case Number
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Status
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Bucket
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Priority
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Overdue Days
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Overdue Amount
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Outstanding
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Actions
              </th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {cases.map((caseItem) => (
              <tr key={caseItem.id} className="hover:bg-gray-50">
                <td className="px-6 py-4 whitespace-nowrap">
                  <div className="text-sm font-medium text-blue-600 cursor-pointer hover:text-blue-800"
                       onClick={() => setSelectedCase(caseItem)}>
                    {caseItem.case_number}
                  </div>
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <span className="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-green-100 text-green-800">
                    {caseItem.case_status}
                  </span>
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${getBucketColor(caseItem.bucket_type)}`}>
                    {caseItem.bucket_type.replace('dpd_', '').replace('_', '-')}
                  </span>
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${getPriorityColor(caseItem.priority)}`}>
                    {caseItem.priority}
                  </span>
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                  {caseItem.overdue_days} days
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                  ₹{Number(caseItem.overdue_amount).toLocaleString('en-IN')}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                  ₹{Number(caseItem.total_outstanding).toLocaleString('en-IN')}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                  <button
                    onClick={() => window.location.href = `/gold-lending/collections/cases/${caseItem.id}`}
                    className="text-blue-600 hover:text-blue-900 mr-3"
                  >
                    View
                  </button>
                  <button
                    onClick={() => setSelectedCase(caseItem)}
                    className="text-green-600 hover:text-green-900"
                  >
                    Update
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>

        {cases.length === 0 && (
          <div className="text-center py-12 text-gray-500">
            No collection cases found
          </div>
        )}
      </div>
    </div>
  );
}
