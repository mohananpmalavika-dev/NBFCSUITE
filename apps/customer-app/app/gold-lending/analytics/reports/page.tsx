'use client';

import React, { useState, useEffect } from 'react';
import { analyticsAPI, Report, ReportExecution } from '../../phase14_analytics_api';

export default function ReportsPage() {
  const [reports, setReports] = useState<Report[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [filterType, setFilterType] = useState<string>('');
  const [filterCategory, setFilterCategory] = useState<string>('');
  const [selectedReport, setSelectedReport] = useState<Report | null>(null);
  const [executions, setExecutions] = useState<ReportExecution[]>([]);

  useEffect(() => {
    loadReports();
  }, [filterType, filterCategory]);

  const loadReports = async () => {
    try {
      setLoading(true);
      const data = await analyticsAPI.listReports({
        report_type: filterType || undefined,
        category: filterCategory || undefined,
      });
      setReports(data);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load reports');
    } finally {
      setLoading(false);
    }
  };

  const handleExecuteReport = async (reportId: string) => {
    try {
      await analyticsAPI.executeReport(reportId, {
        parameters: {},
        filters: {},
        output_format: 'JSON',
      });
      alert('Report execution started successfully!');
    } catch (err) {
      alert('Failed to execute report: ' + (err instanceof Error ? err.message : 'Unknown error'));
    }
  };

  const loadReportExecutions = async (reportId: string) => {
    try {
      const data = await analyticsAPI.listReportExecutions(reportId, { limit: 10 });
      setExecutions(data);
    } catch (err) {
      console.error('Failed to load executions:', err);
    }
  };

  const handleViewReport = async (report: Report) => {
    setSelectedReport(report);
    await loadReportExecutions(report.id);
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'ACTIVE': return 'text-green-600 bg-green-100';
      case 'INACTIVE': return 'text-gray-600 bg-gray-100';
      case 'DRAFT': return 'text-yellow-600 bg-yellow-100';
      default: return 'text-gray-600 bg-gray-100';
    }
  };

  const getExecutionStatusColor = (status?: string) => {
    switch (status) {
      case 'SUCCESS': return 'text-green-600 bg-green-100';
      case 'FAILED': return 'text-red-600 bg-red-100';
      case 'IN_PROGRESS': return 'text-blue-600 bg-blue-100';
      case 'TIMEOUT': return 'text-orange-600 bg-orange-100';
      default: return 'text-gray-600 bg-gray-100';
    }
  };

  if (loading && reports.length === 0) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading reports...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Reports</h1>
          <p className="text-gray-600 mt-1">Custom report builder and management</p>
        </div>
        <button
          className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 flex items-center gap-2"
        >
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
          </svg>
          Create Report
        </button>
      </div>

      {/* Filters */}
      <div className="bg-white rounded-lg shadow p-4 border border-gray-200">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Report Type</label>
            <select
              value={filterType}
              onChange={(e) => setFilterType(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
            >
              <option value="">All Types</option>
              <option value="STANDARD">Standard</option>
              <option value="CUSTOM">Custom</option>
              <option value="ADHOC">Ad-hoc</option>
              <option value="SCHEDULED">Scheduled</option>
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
              <option value="OPERATIONAL">Operational</option>
              <option value="COMPLIANCE">Compliance</option>
              <option value="EXECUTIVE">Executive</option>
            </select>
          </div>

          <div className="flex items-end">
            <button
              onClick={loadReports}
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
          <p className="text-sm text-gray-600">Total Reports</p>
          <p className="text-2xl font-bold text-gray-900 mt-1">{reports.length}</p>
        </div>
        <div className="bg-white rounded-lg shadow p-4 border border-gray-200">
          <p className="text-sm text-gray-600">Active</p>
          <p className="text-2xl font-bold text-green-600 mt-1">
            {reports.filter(r => r.status === 'ACTIVE').length}
          </p>
        </div>
        <div className="bg-white rounded-lg shadow p-4 border border-gray-200">
          <p className="text-sm text-gray-600">Scheduled</p>
          <p className="text-2xl font-bold text-blue-600 mt-1">
            {reports.filter(r => r.schedule_enabled).length}
          </p>
        </div>
        <div className="bg-white rounded-lg shadow p-4 border border-gray-200">
          <p className="text-sm text-gray-600">Custom</p>
          <p className="text-2xl font-bold text-purple-600 mt-1">
            {reports.filter(r => r.report_type === 'CUSTOM').length}
          </p>
        </div>
      </div>

      {/* Reports Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {reports.length === 0 ? (
          <div className="col-span-full bg-white rounded-lg shadow border border-gray-200 p-12">
            <div className="flex flex-col items-center text-center">
              <svg className="w-16 h-16 text-gray-400 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 17v-2m3 2v-4m3 4v-6m2 10H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
              <h3 className="text-lg font-medium text-gray-900">No reports found</h3>
              <p className="text-sm text-gray-500 mt-2">Create your first report to get started with analytics</p>
            </div>
          </div>
        ) : (
          reports.map((report) => (
            <div key={report.id} className="bg-white rounded-lg shadow border border-gray-200 overflow-hidden hover:shadow-lg transition-shadow">
              <div className="p-6">
                <div className="flex items-start justify-between mb-3">
                  <div className="flex-1">
                    <h3 className="text-lg font-semibold text-gray-900 mb-1">{report.report_name}</h3>
                    <p className="text-sm text-gray-500">{report.report_code}</p>
                  </div>
                  <span className={`px-2 py-1 text-xs font-medium rounded-full ${getStatusColor(report.status)}`}>
                    {report.status}
                  </span>
                </div>

                {report.description && (
                  <p className="text-sm text-gray-600 mb-4 line-clamp-2">{report.description}</p>
                )}

                <div className="space-y-2 mb-4">
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-gray-600">Type:</span>
                    <span className="font-medium text-gray-900">{report.report_type}</span>
                  </div>
                  {report.category && (
                    <div className="flex items-center justify-between text-sm">
                      <span className="text-gray-600">Category:</span>
                      <span className="font-medium text-gray-900">{report.category}</span>
                    </div>
                  )}
                  {report.visualization_type && (
                    <div className="flex items-center justify-between text-sm">
                      <span className="text-gray-600">Visualization:</span>
                      <span className="font-medium text-gray-900">{report.visualization_type}</span>
                    </div>
                  )}
                  {report.last_run_at && (
                    <div className="flex items-center justify-between text-sm">
                      <span className="text-gray-600">Last Run:</span>
                      <span className="font-medium text-gray-900">
                        {new Date(report.last_run_at).toLocaleDateString()}
                      </span>
                    </div>
                  )}
                  {report.avg_execution_time_ms && (
                    <div className="flex items-center justify-between text-sm">
                      <span className="text-gray-600">Avg Time:</span>
                      <span className="font-medium text-gray-900">{report.avg_execution_time_ms}ms</span>
                    </div>
                  )}
                </div>

                {report.schedule_enabled && (
                  <div className="bg-blue-50 border border-blue-200 rounded-lg p-2 mb-4">
                    <div className="flex items-center gap-2">
                      <svg className="w-4 h-4 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                      </svg>
                      <span className="text-xs text-blue-800 font-medium">Scheduled Report</span>
                    </div>
                  </div>
                )}

                <div className="flex gap-2">
                  <button
                    onClick={() => handleExecuteReport(report.id)}
                    className="flex-1 px-3 py-2 bg-blue-600 text-white text-sm rounded-lg hover:bg-blue-700 flex items-center justify-center gap-2"
                  >
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z" />
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                    Run
                  </button>
                  <button
                    onClick={() => handleViewReport(report)}
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

      {/* Report Details Modal */}
      {selectedReport && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg max-w-4xl w-full max-h-[90vh] overflow-y-auto">
            <div className="p-6 border-b border-gray-200 flex justify-between items-center">
              <div>
                <h2 className="text-xl font-bold text-gray-900">{selectedReport.report_name}</h2>
                <p className="text-sm text-gray-500 mt-1">{selectedReport.report_code}</p>
              </div>
              <button
                onClick={() => setSelectedReport(null)}
                className="text-gray-400 hover:text-gray-600"
              >
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
            
            <div className="p-6 space-y-6">
              {/* Report Info */}
              <div>
                <h3 className="text-lg font-semibold text-gray-900 mb-3">Report Information</h3>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="text-sm font-medium text-gray-700">Type</label>
                    <p className="text-sm text-gray-900 mt-1">{selectedReport.report_type}</p>
                  </div>
                  <div>
                    <label className="text-sm font-medium text-gray-700">Category</label>
                    <p className="text-sm text-gray-900 mt-1">{selectedReport.category || 'N/A'}</p>
                  </div>
                  <div>
                    <label className="text-sm font-medium text-gray-700">Status</label>
                    <p className="text-sm text-gray-900 mt-1">{selectedReport.status}</p>
                  </div>
                  <div>
                    <label className="text-sm font-medium text-gray-700">Scheduled</label>
                    <p className="text-sm text-gray-900 mt-1">{selectedReport.schedule_enabled ? 'Yes' : 'No'}</p>
                  </div>
                  <div>
                    <label className="text-sm font-medium text-gray-700">Cache Enabled</label>
                    <p className="text-sm text-gray-900 mt-1">{selectedReport.cache_enabled ? 'Yes' : 'No'}</p>
                  </div>
                  <div>
                    <label className="text-sm font-medium text-gray-700">Public</label>
                    <p className="text-sm text-gray-900 mt-1">{selectedReport.is_public ? 'Yes' : 'No'}</p>
                  </div>
                </div>
              </div>

              {/* Recent Executions */}
              <div>
                <h3 className="text-lg font-semibold text-gray-900 mb-3">Recent Executions</h3>
                {executions.length === 0 ? (
                  <p className="text-sm text-gray-500">No executions found</p>
                ) : (
                  <div className="space-y-2">
                    {executions.map((execution) => (
                      <div key={execution.id} className="border border-gray-200 rounded-lg p-3">
                        <div className="flex items-center justify-between mb-2">
                          <span className="text-sm font-medium text-gray-900">{execution.execution_code}</span>
                          <span className={`px-2 py-1 text-xs font-medium rounded-full ${getExecutionStatusColor(execution.result_status)}`}>
                            {execution.result_status || 'PENDING'}
                          </span>
                        </div>
                        <div className="grid grid-cols-3 gap-4 text-xs text-gray-600">
                          <div>
                            <span className="font-medium">Started:</span>{' '}
                            {new Date(execution.started_at).toLocaleString()}
                          </div>
                          {execution.execution_time_ms && (
                            <div>
                              <span className="font-medium">Duration:</span> {execution.execution_time_ms}ms
                            </div>
                          )}
                          {execution.rows_returned !== undefined && (
                            <div>
                              <span className="font-medium">Rows:</span> {execution.rows_returned}
                            </div>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
