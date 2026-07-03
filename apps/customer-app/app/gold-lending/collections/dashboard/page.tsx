'use client';

import { useState, useEffect } from 'react';
import { goldApi } from '../../goldApi';

export default function CollectionsDashboardPage() {
  const [dashboard, setDashboard] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [dateRange, setDateRange] = useState({ from_date: '', to_date: '' });

  useEffect(() => {
    fetchDashboard();
  }, [dateRange]);

  const fetchDashboard = async () => {
    try {
      setLoading(true);
      const data = await goldApi.getCollectionDashboard(dateRange);
      setDashboard(data);
    } catch (error) {
      console.error('Failed to fetch dashboard:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-lg">Loading dashboard...</div>
      </div>
    );
  }

  if (!dashboard) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-lg text-red-600">Failed to load dashboard</div>
      </div>
    );
  }

  const collectionEfficiency = dashboard.total_overdue > 0 
    ? ((dashboard.total_collected / dashboard.total_overdue) * 100).toFixed(2)
    : 0;

  return (
    <div className="p-6 max-w-7xl mx-auto">
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-gray-900">Collections Dashboard</h1>
        <p className="text-gray-600 mt-2">Overview of collection performance and key metrics</p>
      </div>

      {/* Date Range Filter */}
      <div className="bg-white p-4 rounded-lg shadow mb-6">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">From Date</label>
            <input
              type="date"
              value={dateRange.from_date}
              onChange={(e) => setDateRange({ ...dateRange, from_date: e.target.value })}
              className="w-full border border-gray-300 rounded-md px-3 py-2"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">To Date</label>
            <input
              type="date"
              value={dateRange.to_date}
              onChange={(e) => setDateRange({ ...dateRange, to_date: e.target.value })}
              className="w-full border border-gray-300 rounded-md px-3 py-2"
            />
          </div>
          <div className="flex items-end">
            <button
              onClick={() => setDateRange({ from_date: '', to_date: '' })}
              className="w-full bg-gray-200 text-gray-800 px-4 py-2 rounded-md hover:bg-gray-300"
            >
              Clear Filters
            </button>
          </div>
        </div>
      </div>

      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
        <div className="bg-gradient-to-br from-blue-500 to-blue-600 p-6 rounded-lg shadow-lg text-white">
          <div className="text-sm opacity-90 mb-1">Total Cases</div>
          <div className="text-3xl font-bold">{dashboard.total_cases}</div>
          <div className="text-xs opacity-75 mt-2">
            {dashboard.open_cases} Open · {dashboard.closed_cases} Closed
          </div>
        </div>

        <div className="bg-gradient-to-br from-red-500 to-red-600 p-6 rounded-lg shadow-lg text-white">
          <div className="text-sm opacity-90 mb-1">Total Overdue</div>
          <div className="text-3xl font-bold">₹{Number(dashboard.total_overdue).toLocaleString('en-IN', { maximumFractionDigits: 0 })}</div>
          <div className="text-xs opacity-75 mt-2">
            Outstanding: ₹{Number(dashboard.total_outstanding).toLocaleString('en-IN', { maximumFractionDigits: 0 })}
          </div>
        </div>

        <div className="bg-gradient-to-br from-green-500 to-green-600 p-6 rounded-lg shadow-lg text-white">
          <div className="text-sm opacity-90 mb-1">Total Collected</div>
          <div className="text-3xl font-bold">₹{Number(dashboard.total_collected).toLocaleString('en-IN', { maximumFractionDigits: 0 })}</div>
          <div className="text-xs opacity-75 mt-2">
            Collection Rate: {dashboard.collection_rate.toFixed(2)}%
          </div>
        </div>

        <div className="bg-gradient-to-br from-purple-500 to-purple-600 p-6 rounded-lg shadow-lg text-white">
          <div className="text-sm opacity-90 mb-1">Collection Efficiency</div>
          <div className="text-3xl font-bold">{collectionEfficiency}%</div>
          <div className="text-xs opacity-75 mt-2">
            Legal Cases: {dashboard.legal_cases}
          </div>
        </div>
      </div>

      {/* Status Breakdown */}
      <div className="bg-white p-6 rounded-lg shadow mb-6">
        <h2 className="text-xl font-bold text-gray-900 mb-4">Case Status Breakdown</h2>
        <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
          {[
            { label: 'Open', value: dashboard.open_cases, color: 'bg-blue-100 text-blue-800' },
            { label: 'In Progress', value: dashboard.in_progress_cases, color: 'bg-yellow-100 text-yellow-800' },
            { label: 'Legal', value: dashboard.legal_cases, color: 'bg-orange-100 text-orange-800' },
            { label: 'NPA', value: dashboard.npa_cases, color: 'bg-red-100 text-red-800' },
            { label: 'Closed', value: dashboard.closed_cases, color: 'bg-green-100 text-green-800' },
          ].map((status) => (
            <div key={status.label} className="text-center">
              <div className={`${status.color} rounded-lg p-4`}>
                <div className="text-2xl font-bold">{status.value}</div>
                <div className="text-sm font-medium">{status.label}</div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Bucket Analysis */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
        <div className="bg-white p-6 rounded-lg shadow">
          <h2 className="text-xl font-bold text-gray-900 mb-4">DPD Bucket Analysis</h2>
          <div className="space-y-3">
            {[
              { label: '0-30 Days', value: dashboard.bucket_0_30, color: 'bg-yellow-500' },
              { label: '31-60 Days', value: dashboard.bucket_31_60, color: 'bg-orange-500' },
              { label: '61-90 Days', value: dashboard.bucket_61_90, color: 'bg-red-500' },
              { label: '90+ Days', value: dashboard.bucket_90_plus, color: 'bg-purple-500' },
              { label: 'NPA', value: dashboard.npa_cases, color: 'bg-gray-900' },
            ].map((bucket) => {
              const percentage = dashboard.total_cases > 0 
                ? ((bucket.value / dashboard.total_cases) * 100).toFixed(1)
                : 0;
              return (
                <div key={bucket.label}>
                  <div className="flex justify-between items-center mb-1">
                    <span className="text-sm font-medium text-gray-700">{bucket.label}</span>
                    <span className="text-sm font-semibold text-gray-900">{bucket.value} ({percentage}%)</span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div
                      className={`${bucket.color} h-2 rounded-full`}
                      style={{ width: `${percentage}%` }}
                    />
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        <div className="bg-white p-6 rounded-lg shadow">
          <h2 className="text-xl font-bold text-gray-900 mb-4">Collection Summary</h2>
          <div className="space-y-4">
            <div className="flex justify-between items-center p-3 bg-blue-50 rounded-lg">
              <span className="text-sm font-medium text-gray-700">Total Cases</span>
              <span className="text-lg font-bold text-blue-600">{dashboard.total_cases}</span>
            </div>
            <div className="flex justify-between items-center p-3 bg-red-50 rounded-lg">
              <span className="text-sm font-medium text-gray-700">Total Outstanding</span>
              <span className="text-lg font-bold text-red-600">
                ₹{Number(dashboard.total_outstanding).toLocaleString('en-IN')}
              </span>
            </div>
            <div className="flex justify-between items-center p-3 bg-yellow-50 rounded-lg">
              <span className="text-sm font-medium text-gray-700">Total Overdue</span>
              <span className="text-lg font-bold text-yellow-600">
                ₹{Number(dashboard.total_overdue).toLocaleString('en-IN')}
              </span>
            </div>
            <div className="flex justify-between items-center p-3 bg-green-50 rounded-lg">
              <span className="text-sm font-medium text-gray-700">Total Collected</span>
              <span className="text-lg font-bold text-green-600">
                ₹{Number(dashboard.total_collected).toLocaleString('en-IN')}
              </span>
            </div>
            <div className="flex justify-between items-center p-3 bg-purple-50 rounded-lg">
              <span className="text-sm font-medium text-gray-700">Collection Rate</span>
              <span className="text-lg font-bold text-purple-600">
                {dashboard.collection_rate.toFixed(2)}%
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* Quick Actions */}
      <div className="bg-white p-6 rounded-lg shadow">
        <h2 className="text-xl font-bold text-gray-900 mb-4">Quick Actions</h2>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {[
            { label: 'View Cases', href: '/gold-lending/collections/cases', icon: '📋' },
            { label: 'Schedule Visit', href: '/gold-lending/collections/field-visits', icon: '🚗' },
            { label: 'Send Notice', href: '/gold-lending/collections/legal-notices', icon: '📄' },
            { label: 'View Performance', href: '/gold-lending/collections/performance', icon: '📊' },
          ].map((action) => (
            <button
              key={action.label}
              onClick={() => window.location.href = action.href}
              className="flex flex-col items-center justify-center p-4 border-2 border-gray-200 rounded-lg hover:border-blue-500 hover:bg-blue-50 transition-colors"
            >
              <span className="text-3xl mb-2">{action.icon}</span>
              <span className="text-sm font-medium text-gray-700">{action.label}</span>
            </button>
          ))}
        </div>
      </div>
    </div>
  );
}
