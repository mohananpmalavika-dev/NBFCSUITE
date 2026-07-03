'use client';

import { useState, useEffect } from 'react';
import { goldApi } from '../../goldApi';

export default function ReportCatalogPage() {
  const [catalog, setCatalog] = useState<any>(null);
  const [selectedCategory, setSelectedCategory] = useState<string>('all');
  const [searchQuery, setSearchQuery] = useState('');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadCatalog();
  }, [selectedCategory]);

  const loadCatalog = async () => {
    try {
      setLoading(true);
      const data = await goldApi.getReportCatalog(
        selectedCategory === 'all' ? undefined : selectedCategory
      );
      setCatalog(data);
    } catch (error) {
      console.error('Failed to load catalog:', error);
    } finally {
      setLoading(false);
    }
  };

  const categories = [
    { value: 'all', label: 'All Reports', color: 'gray' },
    { value: 'financial', label: 'Financial', color: 'green' },
    { value: 'operational', label: 'Operational', color: 'blue' },
    { value: 'regulatory', label: 'Regulatory', color: 'red' },
    { value: 'custom', label: 'Custom', color: 'purple' },
  ];

  const filteredReports = catalog?.reports?.filter((report: any) =>
    report.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
    report.description?.toLowerCase().includes(searchQuery.toLowerCase())
  ) || [];

  const handleRunReport = (reportCode: string) => {
    window.location.href = `/gold-lending/reporting/builder?report=${reportCode}`;
  };

  if (loading) {
    return (
      <div className="p-6">
        <div className="text-center py-12">Loading report catalog...</div>
      </div>
    );
  }

  return (
    <div className="p-6 max-w-7xl mx-auto">
      {/* Header */}
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-gray-900">Report Catalog</h1>
        <p className="text-gray-600 mt-2">Browse and run standard and custom reports</p>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
        <div className="bg-white rounded-lg shadow p-4">
          <div className="text-sm text-gray-600">Total Reports</div>
          <div className="text-2xl font-bold text-gray-900 mt-1">{catalog?.total_count || 0}</div>
        </div>
        <div className="bg-white rounded-lg shadow p-4">
          <div className="text-sm text-gray-600">System Reports</div>
          <div className="text-2xl font-bold text-blue-600 mt-1">
            {catalog?.reports?.filter((r: any) => r.is_system).length || 0}
          </div>
        </div>
        <div className="bg-white rounded-lg shadow p-4">
          <div className="text-sm text-gray-600">Custom Reports</div>
          <div className="text-2xl font-bold text-purple-600 mt-1">
            {catalog?.reports?.filter((r: any) => !r.is_system).length || 0}
          </div>
        </div>
        <div className="bg-white rounded-lg shadow p-4">
          <div className="text-sm text-gray-600">Most Used</div>
          <div className="text-2xl font-bold text-green-600 mt-1">
            {Math.max(...(catalog?.reports?.map((r: any) => r.execution_count) || [0]))}
          </div>
        </div>
      </div>

      {/* Filters */}
      <div className="bg-white rounded-lg shadow p-4 mb-6">
        <div className="flex flex-col md:flex-row gap-4">
          {/* Category Filter */}
          <div className="flex-1">
            <label className="block text-sm font-medium text-gray-700 mb-2">Category</label>
            <div className="flex flex-wrap gap-2">
              {categories.map((cat) => (
                <button
                  key={cat.value}
                  onClick={() => setSelectedCategory(cat.value)}
                  className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                    selectedCategory === cat.value
                      ? 'bg-blue-600 text-white'
                      : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                  }`}
                >
                  {cat.label}
                </button>
              ))}
            </div>
          </div>

          {/* Search */}
          <div className="flex-1">
            <label className="block text-sm font-medium text-gray-700 mb-2">Search</label>
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search reports..."
              className="w-full border border-gray-300 rounded-lg px-4 py-2"
            />
          </div>
        </div>
      </div>

      {/* Report Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {filteredReports.map((report: any) => (
          <div key={report.id} className="bg-white rounded-lg shadow hover:shadow-lg transition-shadow">
            <div className="p-6">
              {/* Header */}
              <div className="flex items-start justify-between mb-4">
                <div className="flex-1">
                  <h3 className="text-lg font-semibold text-gray-900 mb-1">{report.name}</h3>
                  <p className="text-sm text-gray-600 line-clamp-2">{report.description}</p>
                </div>
                {report.is_system && (
                  <span className="ml-2 inline-flex items-center px-2 py-1 rounded text-xs font-medium bg-blue-100 text-blue-800">
                    System
                  </span>
                )}
              </div>

              {/* Badges */}
              <div className="flex flex-wrap gap-2 mb-4">
                <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                  report.category === 'financial' ? 'bg-green-100 text-green-800' :
                  report.category === 'operational' ? 'bg-blue-100 text-blue-800' :
                  report.category === 'regulatory' ? 'bg-red-100 text-red-800' :
                  'bg-purple-100 text-purple-800'
                }`}>
                  {report.category}
                </span>
                <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-800">
                  {report.report_type}
                </span>
              </div>

              {/* Stats */}
              <div className="grid grid-cols-2 gap-4 mb-4 pb-4 border-b">
                <div>
                  <div className="text-xs text-gray-500">Executions</div>
                  <div className="text-lg font-semibold text-gray-900">{report.execution_count || 0}</div>
                </div>
                <div>
                  <div className="text-xs text-gray-500">Avg Duration</div>
                  <div className="text-lg font-semibold text-gray-900">
                    {report.avg_duration ? `${report.avg_duration}s` : 'N/A'}
                  </div>
                </div>
              </div>

              {/* Parameters */}
              {report.parameter_count > 0 && (
                <div className="mb-4">
                  <div className="text-xs text-gray-500 mb-1">Parameters</div>
                  <div className="text-sm text-gray-700">{report.parameter_count} parameter(s)</div>
                </div>
              )}

              {/* Last Execution */}
              {report.last_execution && (
                <div className="mb-4">
                  <div className="text-xs text-gray-500">Last Executed</div>
                  <div className="text-sm text-gray-700">
                    {new Date(report.last_execution).toLocaleDateString()}
                  </div>
                </div>
              )}

              {/* Actions */}
              <div className="flex gap-2">
                <button
                  onClick={() => handleRunReport(report.code)}
                  className="flex-1 bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors text-sm font-medium"
                >
                  Run Report
                </button>
                <button
                  onClick={() => window.location.href = `/gold-lending/reporting/schedules?report=${report.id}`}
                  className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
                  title="Schedule Report"
                >
                  <svg className="h-5 w-5 text-gray-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                  </svg>
                </button>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Empty State */}
      {filteredReports.length === 0 && (
        <div className="bg-white rounded-lg shadow p-12 text-center">
          <svg className="mx-auto h-12 w-12 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
          <h3 className="mt-2 text-sm font-medium text-gray-900">No reports found</h3>
          <p className="mt-1 text-sm text-gray-500">Try adjusting your filters or search query.</p>
        </div>
      )}
    </div>
  );
}
