'use client';

import { useState, useEffect } from 'react';
import { goldApi } from '../../goldApi';

export default function FieldVisitsPage() {
  const [visits, setVisits] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [filters, setFilters] = useState({
    visit_status: '',
    from_date: '',
    to_date: '',
    skip: 0,
    limit: 50
  });
  const [showCreateModal, setShowCreateModal] = useState(false);

  useEffect(() => {
    fetchVisits();
  }, [filters]);

  const fetchVisits = async () => {
    try {
      setLoading(true);
      const response = await goldApi.getFieldVisits(filters);
      setVisits(response.items || []);
    } catch (error) {
      console.error('Failed to fetch field visits:', error);
    } finally {
      setLoading(false);
    }
  };

  const getStatusColor = (status: string) => {
    const colors: Record<string, string> = {
      'scheduled': 'bg-blue-100 text-blue-800',
      'in_progress': 'bg-yellow-100 text-yellow-800',
      'completed': 'bg-green-100 text-green-800',
      'cancelled': 'bg-red-100 text-red-800',
      'rescheduled': 'bg-purple-100 text-purple-800'
    };
    return colors[status] || 'bg-gray-100 text-gray-800';
  };

  const getOutcomeColor = (outcome: string) => {
    const colors: Record<string, string> = {
      'payment_collected': 'bg-green-100 text-green-800',
      'promise_obtained': 'bg-blue-100 text-blue-800',
      'customer_absent': 'bg-yellow-100 text-yellow-800',
      'dispute': 'bg-red-100 text-red-800',
      'legal_required': 'bg-purple-100 text-purple-800',
      'settled': 'bg-teal-100 text-teal-800'
    };
    return colors[outcome] || 'bg-gray-100 text-gray-800';
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-lg">Loading field visits...</div>
      </div>
    );
  }

  return (
    <div className="p-6 max-w-7xl mx-auto">
      <div className="mb-6 flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Field Visits</h1>
          <p className="text-gray-600 mt-2">Track customer field visits and collection activities</p>
        </div>
        <button
          onClick={() => setShowCreateModal(true)}
          className="bg-blue-600 text-white px-6 py-2 rounded-md hover:bg-blue-700"
        >
          Schedule Visit
        </button>
      </div>

      {/* Filters */}
      <div className="bg-white p-4 rounded-lg shadow mb-6">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Status</label>
            <select
              value={filters.visit_status}
              onChange={(e) => setFilters({ ...filters, visit_status: e.target.value })}
              className="w-full border border-gray-300 rounded-md px-3 py-2"
            >
              <option value="">All Statuses</option>
              <option value="scheduled">Scheduled</option>
              <option value="in_progress">In Progress</option>
              <option value="completed">Completed</option>
              <option value="cancelled">Cancelled</option>
              <option value="rescheduled">Rescheduled</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">From Date</label>
            <input
              type="date"
              value={filters.from_date}
              onChange={(e) => setFilters({ ...filters, from_date: e.target.value })}
              className="w-full border border-gray-300 rounded-md px-3 py-2"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">To Date</label>
            <input
              type="date"
              value={filters.to_date}
              onChange={(e) => setFilters({ ...filters, to_date: e.target.value })}
              className="w-full border border-gray-300 rounded-md px-3 py-2"
            />
          </div>

          <div className="flex items-end">
            <button
              onClick={() => setFilters({ visit_status: '', from_date: '', to_date: '', skip: 0, limit: 50 })}
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
          { label: 'Total Visits', value: visits.length, color: 'blue' },
          { label: 'Scheduled', value: visits.filter(v => v.visit_status === 'scheduled').length, color: 'blue' },
          { label: 'In Progress', value: visits.filter(v => v.visit_status === 'in_progress').length, color: 'yellow' },
          { label: 'Completed', value: visits.filter(v => v.visit_status === 'completed').length, color: 'green' },
          { label: 'Success Rate', value: `${visits.length > 0 ? Math.round(visits.filter(v => v.customer_met).length / visits.length * 100) : 0}%`, color: 'purple' },
        ].map((stat) => (
          <div key={stat.label} className="bg-white p-4 rounded-lg shadow">
            <div className="text-sm text-gray-600">{stat.label}</div>
            <div className="text-2xl font-bold text-gray-900 mt-1">{stat.value}</div>
          </div>
        ))}
      </div>

      {/* Visits Table */}
      <div className="bg-white rounded-lg shadow overflow-hidden">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Visit Number
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Date & Time
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Type
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Status
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Customer Met
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Outcome
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Amount Collected
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Actions
              </th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {visits.map((visit) => (
              <tr key={visit.id} className="hover:bg-gray-50">
                <td className="px-6 py-4 whitespace-nowrap">
                  <div className="text-sm font-medium text-blue-600">
                    {visit.visit_number}
                  </div>
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <div className="text-sm text-gray-900">
                    {new Date(visit.visit_date).toLocaleDateString()}
                  </div>
                  {visit.visit_time && (
                    <div className="text-sm text-gray-500">{visit.visit_time}</div>
                  )}
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <span className="text-sm text-gray-900 capitalize">
                    {visit.visit_type.replace('_', ' ')}
                  </span>
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${getStatusColor(visit.visit_status)}`}>
                    {visit.visit_status}
                  </span>
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${visit.customer_met ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'}`}>
                    {visit.customer_met ? 'Yes' : 'No'}
                  </span>
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  {visit.visit_outcome && (
                    <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${getOutcomeColor(visit.visit_outcome)}`}>
                      {visit.visit_outcome.replace('_', ' ')}
                    </span>
                  )}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                  {visit.amount_collected ? `₹${Number(visit.amount_collected).toLocaleString('en-IN')}` : '-'}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                  <button
                    onClick={() => window.location.href = `/gold-lending/collections/field-visits/${visit.id}`}
                    className="text-blue-600 hover:text-blue-900 mr-3"
                  >
                    View
                  </button>
                  {visit.visit_status === 'scheduled' && (
                    <button
                      onClick={() => goldApi.updateFieldVisit(visit.id, { visit_status: 'in_progress' }).then(fetchVisits)}
                      className="text-green-600 hover:text-green-900"
                    >
                      Start
                    </button>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>

        {visits.length === 0 && (
          <div className="text-center py-12 text-gray-500">
            No field visits found
          </div>
        )}
      </div>
    </div>
  );
}
