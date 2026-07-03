'use client';

import { useState, useEffect } from 'react';
import { goldApi } from '../../goldApi';

export default function AnalyticsPage() {
  const [metrics, setMetrics] = useState<any[]>([]);
  const [selectedMetrics, setSelectedMetrics] = useState<string[]>([]);
  const [dateRange, setDateRange] = useState({
    from: new Date(Date.now() - 30 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
    to: new Date().toISOString().split('T')[0]
  });
  const [groupBy, setGroupBy] = useState('day');
  const [results, setResults] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    loadMetrics();
  }, []);

  const loadMetrics = async () => {
    try {
      const data = await goldApi.getAnalyticsMetrics({ is_active: true });
      setMetrics(data);
    } catch (error) {
      console.error('Failed to load metrics:', error);
    }
  };

  const handleMetricToggle = (metricCode: string) => {
    setSelectedMetrics(prev => 
      prev.includes(metricCode)
        ? prev.filter(m => m !== metricCode)
        : [...prev, metricCode]
    );
  };

  const handleRunQuery = async () => {
    if (selectedMetrics.length === 0) {
      alert('Please select at least one metric');
      return;
    }

    try {
      setLoading(true);
      const data = await goldApi.queryAnalytics({
        metric_codes: selectedMetrics,
        date_from: dateRange.from,
        date_to: dateRange.to,
        group_by: groupBy
      });
      setResults(data);
    } catch (error) {
      console.error('Failed to run query:', error);
      alert('Failed to run analytics query');
    } finally {
      setLoading(false);
    }
  };

  const categoryColors: Record<string, string> = {
    portfolio: 'bg-blue-100 text-blue-800',
    collection: 'bg-green-100 text-green-800',
    risk: 'bg-red-100 text-red-800',
    finance: 'bg-purple-100 text-purple-800',
    operations: 'bg-yellow-100 text-yellow-800'
  };

  return (
    <div className="p-6 max-w-7xl mx-auto">
      {/* Header */}
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-gray-900">Analytics Query Builder</h1>
        <p className="text-gray-600 mt-2">Build custom analytics queries with multiple metrics</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Panel - Metric Selection */}
        <div className="lg:col-span-1">
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">
              Select Metrics ({selectedMetrics.length})
            </h2>

            {/* Group by Category */}
            {['portfolio', 'collection', 'risk', 'finance', 'operations'].map((category) => {
              const categoryMetrics = metrics.filter(m => m.metric_category === category);
              if (categoryMetrics.length === 0) return null;

              return (
                <div key={category} className="mb-4">
                  <div className="text-sm font-medium text-gray-700 mb-2 capitalize">{category}</div>
                  <div className="space-y-2">
                    {categoryMetrics.map((metric) => (
                      <label
                        key={metric.id}
                        className="flex items-start p-3 hover:bg-gray-50 rounded-lg cursor-pointer"
                      >
                        <input
                          type="checkbox"
                          checked={selectedMetrics.includes(metric.metric_code)}
                          onChange={() => handleMetricToggle(metric.metric_code)}
                          className="mt-1 mr-3"
                        />
                        <div className="flex-1">
                          <div className="text-sm font-medium text-gray-900">{metric.metric_name}</div>
                          {metric.description && (
                            <div className="text-xs text-gray-500 mt-1">{metric.description}</div>
                          )}
                          <div className="flex gap-2 mt-1">
                            {metric.is_kpi && (
                              <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-yellow-100 text-yellow-800">
                                KPI
                              </span>
                            )}
                            <span className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-medium ${categoryColors[metric.metric_category]}`}>
                              {metric.metric_type}
                            </span>
                          </div>
                        </div>
                      </label>
                    ))}
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Right Panel - Query Configuration & Results */}
        <div className="lg:col-span-2">
          {/* Query Configuration */}
          <div className="bg-white rounded-lg shadow p-6 mb-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Query Configuration</h2>

            <div className="space-y-4">
              {/* Date Range */}
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">From Date</label>
                  <input
                    type="date"
                    value={dateRange.from}
                    onChange={(e) => setDateRange({ ...dateRange, from: e.target.value })}
                    className="w-full border border-gray-300 rounded-lg px-3 py-2"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">To Date</label>
                  <input
                    type="date"
                    value={dateRange.to}
                    onChange={(e) => setDateRange({ ...dateRange, to: e.target.value })}
                    className="w-full border border-gray-300 rounded-lg px-3 py-2"
                  />
                </div>
              </div>

              {/* Group By */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Group By</label>
                <select
                  value={groupBy}
                  onChange={(e) => setGroupBy(e.target.value)}
                  className="w-full border border-gray-300 rounded-lg px-3 py-2"
                >
                  <option value="day">Daily</option>
                  <option value="week">Weekly</option>
                  <option value="month">Monthly</option>
                  <option value="quarter">Quarterly</option>
                  <option value="branch">By Branch</option>
                  <option value="product">By Product</option>
                </select>
              </div>

              {/* Run Query Button */}
              <button
                onClick={handleRunQuery}
                disabled={loading || selectedMetrics.length === 0}
                className="w-full bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed font-medium transition-colors"
              >
                {loading ? (
                  <span className="flex items-center justify-center">
                    <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                    Running Query...
                  </span>
                ) : (
                  'Run Query'
                )}
              </button>
            </div>
          </div>

          {/* Results */}
          {results && (
            <div className="bg-white rounded-lg shadow">
              <div className="p-6 border-b">
                <div className="flex items-center justify-between">
                  <h2 className="text-lg font-semibold text-gray-900">Query Results</h2>
                  <button className="text-sm text-blue-600 hover:text-blue-700 font-medium">
                    Export to CSV
                  </button>
                </div>
              </div>

              {/* Metrics Summary */}
              <div className="p-6">
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
                  {results.metrics?.map((metric: any) => (
                    <div key={metric.metric_code} className="border border-gray-200 rounded-lg p-4">
                      <div className="text-sm text-gray-600 mb-1">{metric.metric_name}</div>
                      <div className="text-2xl font-bold text-gray-900">{metric.value || 'N/A'}</div>
                      {metric.change_percentage !== null && (
                        <div className="flex items-center text-sm mt-2">
                          <span className={metric.change_percentage >= 0 ? 'text-green-600' : 'text-red-600'}>
                            {metric.change_percentage >= 0 ? '↑' : '↓'} {Math.abs(metric.change_percentage)}%
                          </span>
                          <span className="text-gray-500 ml-1">vs previous</span>
                        </div>
                      )}
                    </div>
                  ))}
                </div>

                {/* Time Series Chart Placeholder */}
                {results.time_series && results.time_series.length > 0 && (
                  <div className="mb-6">
                    <h3 className="text-sm font-medium text-gray-900 mb-3">Trend Over Time</h3>
                    <div className="h-64 bg-gray-50 rounded-lg flex items-center justify-center">
                      <div className="text-gray-500">Chart: Time series visualization</div>
                    </div>
                  </div>
                )}

                {/* Data Table */}
                {results.time_series && results.time_series.length > 0 && (
                  <div>
                    <h3 className="text-sm font-medium text-gray-900 mb-3">Detailed Data</h3>
                    <div className="overflow-x-auto">
                      <table className="min-w-full divide-y divide-gray-200">
                        <thead className="bg-gray-50">
                          <tr>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                              Period
                            </th>
                            {selectedMetrics.map((code) => (
                              <th key={code} className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                                {metrics.find(m => m.metric_code === code)?.metric_name || code}
                              </th>
                            ))}
                          </tr>
                        </thead>
                        <tbody className="bg-white divide-y divide-gray-200">
                          {results.time_series.map((row: any, idx: number) => (
                            <tr key={idx} className="hover:bg-gray-50">
                              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                                {row.period || row.date || row.name}
                              </td>
                              {selectedMetrics.map((code) => (
                                <td key={code} className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                                  {row[code] || '-'}
                                </td>
                              ))}
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Empty State */}
          {!results && (
            <div className="bg-white rounded-lg shadow p-12 text-center">
              <svg className="mx-auto h-12 w-12 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
              </svg>
              <h3 className="mt-2 text-sm font-medium text-gray-900">No Results Yet</h3>
              <p className="mt-1 text-sm text-gray-500">
                Select metrics and run a query to see analytics results
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
