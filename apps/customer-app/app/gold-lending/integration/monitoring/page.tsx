'use client';

import { useEffect, useState } from 'react';
import {
  getIntegrationLogs,
  getIntegrationLog,
  getLogsByCorrelation,
  getLogStatistics,
  getIntegrationConfigurations,
  type IntegrationLog,
  type IntegrationConfiguration,
} from '../../phase13_integration_api';

export default function MonitoringPage() {
  const [logs, setLogs] = useState<IntegrationLog[]>([]);
  const [configurations, setConfigurations] = useState<IntegrationConfiguration[]>([]);
  const [statistics, setStatistics] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [selectedLog, setSelectedLog] = useState<IntegrationLog | null>(null);
  const [autoRefresh, setAutoRefresh] = useState(false);
  const [filters, setFilters] = useState({
    config_id: '',
    status: '',
    start_date: '',
    end_date: '',
    correlation_id: '',
  });

  useEffect(() => {
    loadData();
    const interval = autoRefresh ? setInterval(loadData, 30000) : null;
    return () => { if (interval) clearInterval(interval); };
  }, [autoRefresh, filters]);

  const loadData = async () => {
    try {
      setLoading(true);
      const params: any = { limit: 100 };
      if (filters.config_id) params.config_id = parseInt(filters.config_id);
      if (filters.status) params.status = filters.status;
      if (filters.start_date) params.start_date = filters.start_date;
      if (filters.end_date) params.end_date = filters.end_date;

      const [logsData, configsData, statsData] = await Promise.all([
        filters.correlation_id 
          ? getLogsByCorrelation(filters.correlation_id)
          : getIntegrationLogs(params),
        getIntegrationConfigurations({ limit: 100 }),
        getLogStatistics(),
      ]);
      
      setLogs(logsData);
      setConfigurations(configsData);
      setStatistics(statsData);
    } catch (err) {
      console.error('Failed to load data:', err);
    } finally {
      setLoading(false);
    }
  };

  const viewLogDetails = async (logId: number) => {
    try {
      const log = await getIntegrationLog(logId);
      setSelectedLog(log);
    } catch (err) {
      alert('Failed to load log details');
    }
  };

  const exportToCSV = () => {
    const headers = ['Timestamp', 'Config', 'Method', 'URL', 'Status', 'Response Time', 'Correlation ID'];
    const rows = logs.map(log => [
      new Date(log.request_timestamp).toISOString(),
      configurations.find(c => c.config_id === log.config_id)?.config_name || log.config_id,
      log.request_method,
      log.request_url,
      log.status,
      log.response_time || 0,
      log.correlation_id || ''
    ]);
    
    const csv = [headers, ...rows].map(row => row.join(',')).join('\n');
    const blob = new Blob([csv], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `integration-logs-${new Date().toISOString()}.csv`;
    a.click();
  };

  return (
    <div className="p-6 max-w-7xl mx-auto">
      <div className="mb-6 flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Integration Monitoring</h1>
          <p className="text-gray-600 mt-2">View and analyze integration logs</p>
        </div>
        <div className="flex gap-2">
          <label className="flex items-center gap-2 px-4 py-2 bg-gray-100 rounded cursor-pointer">
            <input type="checkbox" checked={autoRefresh} onChange={(e) => setAutoRefresh(e.target.checked)}/>
            <span className="text-sm">Auto-refresh</span>
          </label>
          <button onClick={exportToCSV} className="px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700">
            Export CSV
          </button>
          <button onClick={loadData} className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700">
            Refresh
          </button>
        </div>
      </div>

      {/* Statistics */}
      {statistics && (
        <div className="grid grid-cols-4 gap-4 mb-6">
          <div className="bg-white rounded-lg shadow p-4">
            <div className="text-sm text-gray-500">Total Requests</div>
            <div className="text-2xl font-bold">{statistics.total_requests || 0}</div>
          </div>
          <div className="bg-white rounded-lg shadow p-4">
            <div className="text-sm text-gray-500">Success Rate</div>
            <div className="text-2xl font-bold text-green-600">{statistics.success_rate?.toFixed(1) || 0}%</div>
          </div>
          <div className="bg-white rounded-lg shadow p-4">
            <div className="text-sm text-gray-500">Failed Requests</div>
            <div className="text-2xl font-bold text-red-600">{statistics.failed_requests || 0}</div>
          </div>
          <div className="bg-white rounded-lg shadow p-4">
            <div className="text-sm text-gray-500">Avg Response Time</div>
            <div className="text-2xl font-bold">{statistics.average_response_time?.toFixed(0) || 0}ms</div>
          </div>
        </div>
      )}

      {/* Filters */}
      <div className="bg-white rounded-lg shadow p-4 mb-6">
        <h3 className="font-semibold mb-3">Filters</h3>
        <div className="grid grid-cols-5 gap-4">
          <select value={filters.config_id} onChange={(e) => setFilters({ ...filters, config_id: e.target.value })}
            className="px-3 py-2 border rounded">
            <option value="">All Configurations</option>
            {configurations.map(c => <option key={c.config_id} value={c.config_id}>{c.config_name}</option>)}
          </select>
          <select value={filters.status} onChange={(e) => setFilters({ ...filters, status: e.target.value })}
            className="px-3 py-2 border rounded">
            <option value="">All Status</option>
            <option value="success">Success</option>
            <option value="failure">Failure</option>
            <option value="pending">Pending</option>
          </select>
          <input type="date" value={filters.start_date}
            onChange={(e) => setFilters({ ...filters, start_date: e.target.value })}
            className="px-3 py-2 border rounded" placeholder="Start Date"/>
          <input type="date" value={filters.end_date}
            onChange={(e) => setFilters({ ...filters, end_date: e.target.value })}
            className="px-3 py-2 border rounded" placeholder="End Date"/>
          <input type="text" value={filters.correlation_id}
            onChange={(e) => setFilters({ ...filters, correlation_id: e.target.value })}
            className="px-3 py-2 border rounded" placeholder="Correlation ID"/>
        </div>
      </div>

      {/* Logs Table */}
      <div className="bg-white rounded-lg shadow overflow-hidden">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Timestamp</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Configuration</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Method</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">URL</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Response Time</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Actions</th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {logs.map((log) => (
              <tr key={log.log_id} className="hover:bg-gray-50">
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  {new Date(log.request_timestamp).toLocaleString()}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                  {configurations.find(c => c.config_id === log.config_id)?.config_name || `ID: ${log.config_id}`}
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <span className="px-2 py-1 text-xs font-semibold rounded bg-blue-100 text-blue-800">
                    {log.request_method}
                  </span>
                </td>
                <td className="px-6 py-4 text-sm text-gray-900 max-w-xs truncate">
                  {log.request_url}
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <span className={`px-2 py-1 text-xs font-semibold rounded-full ${
                    log.status === 'success' ? 'bg-green-100 text-green-800' :
                    log.status === 'failure' ? 'bg-red-100 text-red-800' :
                    'bg-yellow-100 text-yellow-800'
                  }`}>
                    {log.status}
                  </span>
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                  {log.response_time ? `${log.response_time}ms` : '-'}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm font-medium space-x-2">
                  <button onClick={() => viewLogDetails(log.log_id)} className="text-blue-600 hover:text-blue-900">
                    Details
                  </button>
                  {log.correlation_id && (
                    <button onClick={() => setFilters({ ...filters, correlation_id: log.correlation_id || '' })}
                      className="text-purple-600 hover:text-purple-900">
                      Related
                    </button>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
        {logs.length === 0 && (
          <div className="text-center py-12 text-gray-500">
            {loading ? 'Loading logs...' : 'No logs found'}
          </div>
        )}
      </div>

      {/* Log Details Modal */}
      {selectedLog && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 max-w-4xl w-full max-h-[90vh] overflow-y-auto">
            <h2 className="text-2xl font-bold mb-4">Log Details</h2>
            <div className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700">Log ID</label>
                  <div className="text-sm text-gray-900">{selectedLog.log_id}</div>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700">Correlation ID</label>
                  <div className="text-sm text-gray-900 font-mono">{selectedLog.correlation_id || 'N/A'}</div>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700">Request Timestamp</label>
                  <div className="text-sm text-gray-900">{new Date(selectedLog.request_timestamp).toLocaleString()}</div>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700">Response Timestamp</label>
                  <div className="text-sm text-gray-900">
                    {selectedLog.response_timestamp ? new Date(selectedLog.response_timestamp).toLocaleString() : 'N/A'}
                  </div>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700">Status</label>
                  <span className={`px-2 py-1 text-xs font-semibold rounded-full ${
                    selectedLog.status === 'success' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                  }`}>
                    {selectedLog.status}
                  </span>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700">Response Time</label>
                  <div className="text-sm text-gray-900">{selectedLog.response_time || 0}ms</div>
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Request Details</label>
                <div className="bg-gray-50 p-3 rounded border">
                  <div className="text-sm"><strong>Method:</strong> {selectedLog.request_method}</div>
                  <div className="text-sm"><strong>URL:</strong> {selectedLog.request_url}</div>
                  {selectedLog.request_headers && (
                    <div className="text-sm mt-2">
                      <strong>Headers:</strong>
                      <pre className="mt-1 text-xs bg-white p-2 rounded border overflow-auto">
                        {JSON.stringify(selectedLog.request_headers, null, 2)}
                      </pre>
                    </div>
                  )}
                  {selectedLog.request_body && (
                    <div className="text-sm mt-2">
                      <strong>Body:</strong>
                      <pre className="mt-1 text-xs bg-white p-2 rounded border overflow-auto max-h-40">
                        {JSON.stringify(selectedLog.request_body, null, 2)}
                      </pre>
                    </div>
                  )}
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Response Details</label>
                <div className="bg-gray-50 p-3 rounded border">
                  {selectedLog.response_status && (
                    <div className="text-sm"><strong>Status Code:</strong> {selectedLog.response_status}</div>
                  )}
                  {selectedLog.response_body && (
                    <div className="text-sm mt-2">
                      <strong>Body:</strong>
                      <pre className="mt-1 text-xs bg-white p-2 rounded border overflow-auto max-h-40">
                        {JSON.stringify(selectedLog.response_body, null, 2)}
                      </pre>
                    </div>
                  )}
                  {selectedLog.error_message && (
                    <div className="text-sm mt-2">
                      <strong className="text-red-600">Error:</strong>
                      <div className="mt-1 text-red-600 bg-red-50 p-2 rounded border border-red-200">
                        {selectedLog.error_message}
                      </div>
                    </div>
                  )}
                </div>
              </div>
            </div>

            <div className="flex justify-end mt-6">
              <button onClick={() => setSelectedLog(null)}
                className="px-4 py-2 bg-gray-600 text-white rounded hover:bg-gray-700">
                Close
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
