'use client';

import React, { useState, useEffect } from 'react';
import { analyticsAPI, Dashboard } from '../../phase14_analytics_api';

export default function DashboardsPage() {
  const [dashboards, setDashboards] = useState<Dashboard[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [filterType, setFilterType] = useState<string>('');
  const [filterCategory, setFilterCategory] = useState<string>('');
  const [selectedDashboard, setSelectedDashboard] = useState<Dashboard | null>(null);

  useEffect(() => {
    loadDashboards();
  }, [filterType, filterCategory]);

  const loadDashboards = async () => {
    try {
      setLoading(true);
      const data = await analyticsAPI.listDashboards({
        dashboard_type: filterType || undefined,
        category: filterCategory || undefined,
      });
      setDashboards(data);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load dashboards');
    } finally {
      setLoading(false);
    }
  };

  const handleRefresh = async (id: string) => {
    try {
      await analyticsAPI.refreshDashboard(id);
      await loadDashboards();
    } catch (err) {
      alert('Failed to refresh dashboard: ' + (err instanceof Error ? err.message : 'Unknown error'));
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'ACTIVE': return 'text-green-600 bg-green-100';
      case 'INACTIVE': return 'text-gray-600 bg-gray-100';
      case 'DRAFT': return 'text-yellow-600 bg-yellow-100';
      default: return 'text-gray-600 bg-gray-100';
    }
  };

  if (loading && dashboards.length === 0) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading dashboards...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Dashboards</h1>
          <p className="text-gray-600 mt-1">Executive and operational visualization dashboards</p>
        </div>
        <button className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 flex items-center gap-2">
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
          </svg>
          Create Dashboard
        </button>
      </div>

      {/* Filters */}
      <div className="bg-white rounded-lg shadow p-4 border border-gray-200">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Dashboard Type</label>
            <select
              value={filterType}
              onChange={(e) => setFilterType(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
            >
              <option value="">All Types</option>
              <option value="EXECUTIVE">Executive</option>
              <option value="OPERATIONAL">Operational</option>
              <option value="ANALYTICAL">Analytical</option>
              <option value="REAL_TIME">Real-time</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Category</label>
            <select
              value={filterCategory}
              onChange={(e) => setFilterCategory(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
            >
              <option value="">All Categories</option>
              <option value="FINANCIAL">Financial</option>
              <option value="OPERATIONS">Operations</option>
              <option value="SALES">Sales</option>
              <option value="MARKETING">Marketing</option>
            </select>
          </div>

          <div className="flex items-end">
            <button
              onClick={loadDashboards}
              className="w-full px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200"
            >
              Apply Filters
            </button>
          </div>
        </div>
      </div>

      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <p className="text-red-600">{error}</p>
        </div>
      )}

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-white rounded-lg shadow p-4 border border-gray-200">
          <p className="text-sm text-gray-600">Total Dashboards</p>
          <p className="text-2xl font-bold text-gray-900 mt-1">{dashboards.length}</p>
        </div>
        <div className="bg-white rounded-lg shadow p-4 border border-gray-200">
          <p className="text-sm text-gray-600">Active</p>
          <p className="text-2xl font-bold text-green-600 mt-1">
            {dashboards.filter(d => d.status === 'ACTIVE').length}
          </p>
        </div>
        <div className="bg-white rounded-lg shadow p-4 border border-gray-200">
          <p className="text-sm text-gray-600">Total Views</p>
          <p className="text-2xl font-bold text-blue-600 mt-1">
            {dashboards.reduce((sum, d) => sum + d.view_count, 0).toLocaleString()}
          </p>
        </div>
        <div className="bg-white rounded-lg shadow p-4 border border-gray-200">
          <p className="text-sm text-gray-600">Real-time</p>
          <p className="text-2xl font-bold text-purple-600 mt-1">
            {dashboards.filter(d => d.dashboard_type === 'REAL_TIME').length}
          </p>
        </div>
      </div>

      {/* Dashboards Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {dashboards.length === 0 ? (
          <div className="col-span-full bg-white rounded-lg shadow border border-gray-200 p-12">
            <div className="flex flex-col items-center text-center">
              <svg className="w-16 h-16 text-gray-400 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
              </svg>
              <h3 className="text-lg font-medium text-gray-900">No dashboards found</h3>
              <p className="text-sm text-gray-500 mt-2">Create your first dashboard to visualize your data</p>
            </div>
          </div>
        ) : (
          dashboards.map((dashboard) => (
            <div key={dashboard.id} className="bg-white rounded-lg shadow border border-gray-200 overflow-hidden hover:shadow-lg transition-shadow">
              <div className="h-40 bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center">
                <div className="text-center text-white">
                  <svg className="w-16 h-16 mx-auto mb-2 opacity-80" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                  </svg>
                  <p className="text-sm font-medium">{dashboard.widgets?.length || 0} Widgets</p>
                </div>
              </div>
              
              <div className="p-6">
                <div className="flex items-start justify-between mb-3">
                  <div className="flex-1">
                    <h3 className="text-lg font-semibold text-gray-900 mb-1">{dashboard.dashboard_name}</h3>
                    <p className="text-sm text-gray-500">{dashboard.dashboard_code}</p>
                  </div>
                  <span className={`px-2 py-1 text-xs font-medium rounded-full ${getStatusColor(dashboard.status)}`}>
                    {dashboard.status}
                  </span>
                </div>

                {dashboard.description && (
                  <p className="text-sm text-gray-600 mb-4 line-clamp-2">{dashboard.description}</p>
                )}

                <div className="space-y-2 mb-4">
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-gray-600">Type:</span>
                    <span className="font-medium text-gray-900">{dashboard.dashboard_type}</span>
                  </div>
                  {dashboard.category && (
                    <div className="flex items-center justify-between text-sm">
                      <span className="text-gray-600">Category:</span>
                      <span className="font-medium text-gray-900">{dashboard.category}</span>
                    </div>
                  )}
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-gray-600">Views:</span>
                    <span className="font-medium text-gray-900">{dashboard.view_count.toLocaleString()}</span>
                  </div>
                  {dashboard.last_viewed_at && (
                    <div className="flex items-center justify-between text-sm">
                      <span className="text-gray-600">Last Viewed:</span>
                      <span className="font-medium text-gray-900">
                        {new Date(dashboard.last_viewed_at).toLocaleDateString()}
                      </span>
                    </div>
                  )}
                </div>

                {dashboard.auto_refresh && (
                  <div className="bg-green-50 border border-green-200 rounded-lg p-2 mb-4">
                    <div className="flex items-center gap-2">
                      <svg className="w-4 h-4 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                      </svg>
                      <span className="text-xs text-green-800 font-medium">
                        Auto-refresh: {dashboard.refresh_interval_seconds}s
                      </span>
                    </div>
                  </div>
                )}

                <div className="flex gap-2">
                  <button
                    onClick={() => handleRefresh(dashboard.id)}
                    className="flex-1 px-3 py-2 bg-blue-600 text-white text-sm rounded-lg hover:bg-blue-700 flex items-center justify-center gap-2"
                  >
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                    </svg>
                    Refresh
                  </button>
                  <button
                    onClick={() => setSelectedDashboard(dashboard)}
                    className="flex-1 px-3 py-2 bg-gray-100 text-gray-700 text-sm rounded-lg hover:bg-gray-200"
                  >
                    View
                  </button>
                </div>
              </div>
            </div>
          ))
        )}
      </div>

      {/* Dashboard Details Modal */}
      {selectedDashboard && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg max-w-4xl w-full max-h-[90vh] overflow-y-auto">
            <div className="p-6 border-b border-gray-200 flex justify-between items-center">
              <div>
                <h2 className="text-xl font-bold text-gray-900">{selectedDashboard.dashboard_name}</h2>
                <p className="text-sm text-gray-500 mt-1">{selectedDashboard.dashboard_code}</p>
              </div>
              <button
                onClick={() => setSelectedDashboard(null)}
                className="text-gray-400 hover:text-gray-600"
              >
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
            
            <div className="p-6 space-y-6">
              {/* Dashboard Info */}
              <div>
                <h3 className="text-lg font-semibold text-gray-900 mb-3">Dashboard Information</h3>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="text-sm font-medium text-gray-700">Type</label>
                    <p className="text-sm text-gray-900 mt-1">{selectedDashboard.dashboard_type}</p>
                  </div>
                  <div>
                    <label className="text-sm font-medium text-gray-700">Category</label>
                    <p className="text-sm text-gray-900 mt-1">{selectedDashboard.category || 'N/A'}</p>
                  </div>
                  <div>
                    <label className="text-sm font-medium text-gray-700">Status</label>
                    <p className="text-sm text-gray-900 mt-1">{selectedDashboard.status}</p>
                  </div>
                  <div>
                    <label className="text-sm font-medium text-gray-700">Layout Type</label>
                    <p className="text-sm text-gray-900 mt-1">{selectedDashboard.layout_type || 'N/A'}</p>
                  </div>
                  <div>
                    <label className="text-sm font-medium text-gray-700">Theme</label>
                    <p className="text-sm text-gray-900 mt-1">{selectedDashboard.theme}</p>
                  </div>
                  <div>
                    <label className="text-sm font-medium text-gray-700">Mobile Optimized</label>
                    <p className="text-sm text-gray-900 mt-1">{selectedDashboard.mobile_optimized ? 'Yes' : 'No'}</p>
                  </div>
                  <div>
                    <label className="text-sm font-medium text-gray-700">View Count</label>
                    <p className="text-sm text-gray-900 mt-1">{selectedDashboard.view_count.toLocaleString()}</p>
                  </div>
                  <div>
                    <label className="text-sm font-medium text-gray-700">Avg Load Time</label>
                    <p className="text-sm text-gray-900 mt-1">
                      {selectedDashboard.avg_load_time_ms ? `${selectedDashboard.avg_load_time_ms}ms` : 'N/A'}
                    </p>
                  </div>
                </div>
              </div>

              {/* Widgets */}
              <div>
                <h3 className="text-lg font-semibold text-gray-900 mb-3">
                  Widgets ({selectedDashboard.widgets?.length || 0})
                </h3>
                {selectedDashboard.widgets && selectedDashboard.widgets.length > 0 ? (
                  <div className="grid grid-cols-2 gap-3">
                    {selectedDashboard.widgets.map((widget: any, index: number) => (
                      <div key={index} className="border border-gray-200 rounded-lg p-3">
                        <div className="flex items-center gap-2 mb-2">
                          <svg className="w-5 h-5 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 12l3-3 3 3 4-4M8 21l4-4 4 4M3 4h18M4 4h16v12a1 1 0 01-1 1H5a1 1 0 01-1-1V4z" />
                          </svg>
                          <span className="text-sm font-medium text-gray-900">
                            Widget {index + 1}
                          </span>
                        </div>
                        <p className="text-xs text-gray-600">
                          {widget.type || 'Unknown Type'}
                        </p>
                      </div>
                    ))}
                  </div>
                ) : (
                  <p className="text-sm text-gray-500">No widgets configured</p>
                )}
              </div>

              {/* Auto-refresh Settings */}
              {selectedDashboard.auto_refresh && (
                <div>
                  <h3 className="text-lg font-semibold text-gray-900 mb-3">Refresh Settings</h3>
                  <div className="bg-green-50 border border-green-200 rounded-lg p-4">
                    <div className="flex items-center gap-3">
                      <svg className="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                      </svg>
                      <div>
                        <p className="text-sm font-medium text-green-900">Auto-refresh enabled</p>
                        <p className="text-sm text-green-700">
                          Refreshes every {selectedDashboard.refresh_interval_seconds} seconds
                        </p>
                      </div>
                    </div>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
