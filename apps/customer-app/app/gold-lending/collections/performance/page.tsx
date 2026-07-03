'use client';

import { useState, useEffect } from 'react';
import { goldApi } from '../../goldApi';

export default function PerformanceDashboardPage() {
  const [performance, setPerformance] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [filters, setFilters] = useState({ team_name: '', region: '', skip: 0, limit: 50 });

  useEffect(() => {
    goldApi.getPerformanceRecords(filters)
      .then(data => setPerformance(data))
      .catch(console.error)
      .finally(() => setLoading(false));
  }, [filters]);

  const getRatingColor = (rating: string) => {
    const colors: Record<string, string> = {
      'poor': 'bg-red-100 text-red-800',
      'below_average': 'bg-orange-100 text-orange-800',
      'average': 'bg-yellow-100 text-yellow-800',
      'good': 'bg-blue-100 text-blue-800',
      'excellent': 'bg-green-100 text-green-800',
      'outstanding': 'bg-purple-100 text-purple-800'
    };
    return colors[rating] || 'bg-gray-100 text-gray-800';
  };

  if (loading) return <div className="flex items-center justify-center min-h-screen"><div className="text-lg">Loading...</div></div>;

  const totalCollected = performance.reduce((sum, p) => sum + Number(p.total_collected_amount || 0), 0);
  const totalOverdue = performance.reduce((sum, p) => sum + Number(p.total_overdue_amount || 0), 0);
  const avgCollectionRate = performance.length > 0
    ? performance.reduce((sum, p) => sum + Number(p.collection_percentage || 0), 0) / performance.length
    : 0;

  return (
    <div className="p-6 max-w-7xl mx-auto">
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-gray-900">Collection Performance</h1>
        <p className="text-gray-600 mt-2">Track team and individual collection performance metrics</p>
      </div>

      <div className="bg-white p-4 rounded-lg shadow mb-6">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <input
            type="text"
            placeholder="Team Name"
            value={filters.team_name}
            onChange={(e) => setFilters({ ...filters, team_name: e.target.value })}
            className="border border-gray-300 rounded-md px-3 py-2"
          />
          <input
            type="text"
            placeholder="Region"
            value={filters.region}
            onChange={(e) => setFilters({ ...filters, region: e.target.value })}
            className="border border-gray-300 rounded-md px-3 py-2"
          />
          <button
            onClick={() => setFilters({ team_name: '', region: '', skip: 0, limit: 50 })}
            className="bg-gray-200 text-gray-800 px-4 py-2 rounded-md hover:bg-gray-300"
          >
            Clear
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
        {[
          { label: 'Total Collected', value: `₹${totalCollected.toLocaleString('en-IN')}` },
          { label: 'Total Overdue', value: `₹${totalOverdue.toLocaleString('en-IN')}` },
          { label: 'Avg Collection Rate', value: `${avgCollectionRate.toFixed(2)}%` },
          { label: 'Total Records', value: performance.length },
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
              {['User', 'Team/Region', 'Period', 'Cases Assigned', 'Cases Resolved', 'Overdue Amount', 'Collected', 'Collection %', 'Field Visits', 'Promises Kept', 'Rating', 'Incentive'].map(header => (
                <th key={header} className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">{header}</th>
              ))}
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {performance.map(perf => (
              <tr key={perf.id} className="hover:bg-gray-50">
                <td className="px-6 py-4 whitespace-nowrap">
                  <div className="text-sm font-medium text-gray-900">{perf.user_name}</div>
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <div className="text-sm text-gray-900">{perf.team_name || '-'}</div>
                  <div className="text-sm text-gray-500">{perf.region || '-'}</div>
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm">
                  <div>{new Date(perf.period_start).toLocaleDateString()}</div>
                  <div className="text-gray-500">to</div>
                  <div>{new Date(perf.period_end).toLocaleDateString()}</div>
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm">{perf.total_cases_assigned}</td>
                <td className="px-6 py-4 whitespace-nowrap text-sm">{perf.total_cases_resolved}</td>
                <td className="px-6 py-4 whitespace-nowrap text-sm">₹{Number(perf.total_overdue_amount).toLocaleString('en-IN')}</td>
                <td className="px-6 py-4 whitespace-nowrap text-sm font-semibold text-green-600">
                  ₹{Number(perf.total_collected_amount).toLocaleString('en-IN')}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm font-semibold">
                  {perf.collection_percentage ? `${perf.collection_percentage}%` : '-'}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm">
                  {perf.successful_field_visits}/{perf.total_field_visits}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm">
                  {perf.promises_kept}/{perf.total_promises_obtained}
                  {perf.promise_kept_rate && (
                    <div className="text-xs text-gray-500">({perf.promise_kept_rate}%)</div>
                  )}
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  {perf.performance_rating && (
                    <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${getRatingColor(perf.performance_rating)}`}>
                      {perf.performance_rating.replace('_', ' ')}
                    </span>
                  )}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm font-semibold text-blue-600">
                  {perf.incentive_earned ? `₹${Number(perf.incentive_earned).toLocaleString('en-IN')}` : '-'}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
        {performance.length === 0 && <div className="text-center py-12 text-gray-500">No performance records found</div>}
      </div>
    </div>
  );
}
