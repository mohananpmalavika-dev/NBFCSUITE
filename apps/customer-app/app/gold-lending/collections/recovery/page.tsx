'use client';

import { useState, useEffect } from 'react';
import { goldApi } from '../../goldApi';

export default function RecoveryActionsPage() {
  const [actions, setActions] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [filters, setFilters] = useState({ action_type: '', action_status: '', skip: 0, limit: 50 });

  useEffect(() => {
    goldApi.getRecoveryActions(filters)
      .then(data => setActions(data))
      .catch(console.error)
      .finally(() => setLoading(false));
  }, [filters]);

  const getStatusColor = (status: string) => {
    const colors: Record<string, string> = {
      'planned': 'bg-gray-100 text-gray-800',
      'approved': 'bg-blue-100 text-blue-800',
      'in_progress': 'bg-yellow-100 text-yellow-800',
      'completed': 'bg-green-100 text-green-800',
      'cancelled': 'bg-red-100 text-red-800',
      'failed': 'bg-purple-100 text-purple-800'
    };
    return colors[status] || 'bg-gray-100 text-gray-800';
  };

  if (loading) return <div className="flex items-center justify-center min-h-screen"><div className="text-lg">Loading...</div></div>;

  return (
    <div className="p-6 max-w-7xl mx-auto">
      <div className="mb-6 flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Recovery Actions</h1>
          <p className="text-gray-600 mt-2">Track recovery and repossession activities</p>
        </div>
        <button className="bg-blue-600 text-white px-6 py-2 rounded-md hover:bg-blue-700">Create Action</button>
      </div>

      <div className="bg-white p-4 rounded-lg shadow mb-6">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <select
            value={filters.action_type}
            onChange={(e) => setFilters({ ...filters, action_type: e.target.value })}
            className="border border-gray-300 rounded-md px-3 py-2"
          >
            <option value="">All Types</option>
            <option value="reminder">Reminder</option>
            <option value="notice">Notice</option>
            <option value="repossession">Repossession</option>
            <option value="seizure">Seizure</option>
            <option value="auction_prep">Auction Prep</option>
            <option value="legal_filing">Legal Filing</option>
            <option value="settlement">Settlement</option>
          </select>
          <select
            value={filters.action_status}
            onChange={(e) => setFilters({ ...filters, action_status: e.target.value })}
            className="border border-gray-300 rounded-md px-3 py-2"
          >
            <option value="">All Statuses</option>
            <option value="planned">Planned</option>
            <option value="approved">Approved</option>
            <option value="in_progress">In Progress</option>
            <option value="completed">Completed</option>
            <option value="cancelled">Cancelled</option>
            <option value="failed">Failed</option>
          </select>
          <button
            onClick={() => setFilters({ action_type: '', action_status: '', skip: 0, limit: 50 })}
            className="bg-gray-200 text-gray-800 px-4 py-2 rounded-md hover:bg-gray-300"
          >
            Clear
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-5 gap-4 mb-6">
        {[
          { label: 'Total Actions', value: actions.length },
          { label: 'Planned', value: actions.filter(a => a.action_status === 'planned').length },
          { label: 'In Progress', value: actions.filter(a => a.action_status === 'in_progress').length },
          { label: 'Completed', value: actions.filter(a => a.action_status === 'completed').length },
          { label: 'Success Rate', value: `${actions.length > 0 ? Math.round(actions.filter(a => a.outcome === 'successful').length / actions.length * 100) : 0}%` },
        ].map(stat => (
          <div key={stat.label} className="bg-white p-4 rounded-lg shadow">
            <div className="text-sm text-gray-600">{stat.label}</div>
            <div className="text-2xl font-bold text-gray-900 mt-1">{stat.value}</div>
          </div>
        ))}
      </div>

      <div className="bg-white rounded-lg shadow overflow-hidden">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              {['Action Number', 'Type', 'Date', 'Status', 'Description', 'Estimated Value', 'Outcome', 'Police Assist', 'Actions'].map(header => (
                <th key={header} className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">{header}</th>
              ))}
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {actions.map(action => (
              <tr key={action.id} className="hover:bg-gray-50">
                <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-blue-600">{action.action_number}</td>
                <td className="px-6 py-4 whitespace-nowrap text-sm capitalize">{action.action_type.replace('_', ' ')}</td>
                <td className="px-6 py-4 whitespace-nowrap text-sm">{new Date(action.action_date).toLocaleDateString()}</td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${getStatusColor(action.action_status)}`}>
                    {action.action_status}
                  </span>
                </td>
                <td className="px-6 py-4 text-sm max-w-xs truncate">{action.action_description}</td>
                <td className="px-6 py-4 whitespace-nowrap text-sm">
                  {action.estimated_value ? `₹${Number(action.estimated_value).toLocaleString('en-IN')}` : '-'}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm capitalize">
                  {action.outcome ? action.outcome.replace('_', ' ') : '-'}
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${action.police_assistance ? 'bg-red-100 text-red-800' : 'bg-gray-100 text-gray-800'}`}>
                    {action.police_assistance ? 'Yes' : 'No'}
                  </span>
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                  <button className="text-blue-600 hover:text-blue-900 mr-3">View</button>
                  {action.action_status === 'planned' && (
                    <button className="text-green-600 hover:text-green-900">Approve</button>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
        {actions.length === 0 && <div className="text-center py-12 text-gray-500">No recovery actions found</div>}
      </div>
    </div>
  );
}
