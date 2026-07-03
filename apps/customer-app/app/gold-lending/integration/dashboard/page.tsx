'use client';

import { useEffect, useState } from 'react';
import {
  getIntegrationStatistics,
  getProviderPerformance,
  getWebhookHealth,
  getQueueSummary,
  type IntegrationStatistics,
  type ProviderPerformance,
  type WebhookHealth,
  type QueueSummary,
} from '../../phase13_integration_api';

export default function IntegrationDashboardPage() {
  const [statistics, setStatistics] = useState<IntegrationStatistics | null>(null);
  const [providers, setProviders] = useState<ProviderPerformance[]>([]);
  const [webhookHealth, setWebhookHealth] = useState<WebhookHealth | null>(null);
  const [queueSummary, setQueueSummary] = useState<QueueSummary | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    try {
      setLoading(true);
      setError(null);

      const [statsData, providersData, webhookData, queueData] = await Promise.all([
        getIntegrationStatistics(),
        getProviderPerformance(),
        getWebhookHealth(),
        getQueueSummary(),
      ]);

      setStatistics(statsData);
      setProviders(providersData);
      setWebhookHealth(webhookData);
      setQueueSummary(queueData);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load dashboard data');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading dashboard...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-6">
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
          <p className="font-bold">Error</p>
          <p>{error}</p>
          <button
            onClick={loadDashboardData}
            className="mt-2 bg-red-600 text-white px-4 py-2 rounded hover:bg-red-700"
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="p-6 max-w-7xl mx-auto">
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-gray-900">Integration Hub Dashboard</h1>
        <p className="text-gray-600 mt-2">Monitor external integrations, webhooks, and message queue</p>
      </div>

      {/* Overall Statistics */}
      {statistics && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-6">
          <div className="bg-white rounded-lg shadow p-6">
            <div className="text-sm font-medium text-gray-500 mb-1">Total Requests</div>
            <div className="text-3xl font-bold text-gray-900">{statistics.total_requests.toLocaleString()}</div>
            <div className="text-xs text-gray-500 mt-2">
              Success: {statistics.successful_requests} | Failed: {statistics.failed_requests}
            </div>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <div className="text-sm font-medium text-gray-500 mb-1">Avg Response Time</div>
            <div className="text-3xl font-bold text-gray-900">{statistics.average_response_time.toFixed(0)}ms</div>
            <div className="text-xs text-green-600 mt-2">
              Success Rate: {statistics.total_requests > 0 
                ? ((statistics.successful_requests / statistics.total_requests) * 100).toFixed(1) 
                : 0}%
            </div>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <div className="text-sm font-medium text-gray-500 mb-1">Active Configurations</div>
            <div className="text-3xl font-bold text-gray-900">{statistics.active_configurations}</div>
            <div className="text-xs text-gray-500 mt-2">Integration configs</div>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <div className="text-sm font-medium text-gray-500 mb-1">Pending Messages</div>
            <div className="text-3xl font-bold text-gray-900">{statistics.pending_messages}</div>
            <div className="text-xs text-gray-500 mt-2">In message queue</div>
          </div>
        </div>
      )}

      {/* Provider Performance */}
      {providers.length > 0 && (
        <div className="bg-white rounded-lg shadow mb-6">
          <div className="px-6 py-4 border-b border-gray-200">
            <h2 className="text-xl font-semibold text-gray-900">Provider Performance</h2>
          </div>
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Provider</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Total Calls</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Success Rate</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Avg Response</th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {providers.map((provider) => (
                  <tr key={provider.provider_id} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm font-medium text-gray-900">{provider.provider_name}</div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {provider.total_calls.toLocaleString()}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`px-2 py-1 text-xs font-semibold rounded-full ${
                        provider.success_rate >= 95 ? 'bg-green-100 text-green-800' :
                        provider.success_rate >= 80 ? 'bg-yellow-100 text-yellow-800' :
                        'bg-red-100 text-red-800'
                      }`}>
                        {provider.success_rate.toFixed(1)}%
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {provider.average_response_time.toFixed(0)}ms
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Webhook Health */}
        {webhookHealth && (
          <div className="bg-white rounded-lg shadow">
            <div className="px-6 py-4 border-b border-gray-200">
              <h2 className="text-xl font-semibold text-gray-900">Webhook Health</h2>
            </div>
            <div className="p-6">
              <div className="space-y-4">
                <div className="flex justify-between items-center">
                  <span className="text-sm text-gray-600">Total Deliveries</span>
                  <span className="text-lg font-semibold">{webhookHealth.total_deliveries.toLocaleString()}</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-sm text-gray-600">Successful</span>
                  <span className="text-lg font-semibold text-green-600">{webhookHealth.successful_deliveries.toLocaleString()}</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-sm text-gray-600">Failed</span>
                  <span className="text-lg font-semibold text-red-600">{webhookHealth.failed_deliveries.toLocaleString()}</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-sm text-gray-600">Pending</span>
                  <span className="text-lg font-semibold text-yellow-600">{webhookHealth.pending_deliveries.toLocaleString()}</span>
                </div>
                <div className="pt-4 border-t">
                  <div className="flex justify-between items-center">
                    <span className="text-sm text-gray-600">Success Rate</span>
                    <span className="text-lg font-semibold">{webhookHealth.success_rate.toFixed(1)}%</span>
                  </div>
                  <div className="flex justify-between items-center mt-2">
                    <span className="text-sm text-gray-600">Avg Response Time</span>
                    <span className="text-lg font-semibold">{webhookHealth.average_response_time.toFixed(0)}ms</span>
                  </div>
                  <div className="flex justify-between items-center mt-2">
                    <span className="text-sm text-gray-600">Total Retries</span>
                    <span className="text-lg font-semibold">{webhookHealth.total_retries.toLocaleString()}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Queue Summary */}
        {queueSummary && (
          <div className="bg-white rounded-lg shadow">
            <div className="px-6 py-4 border-b border-gray-200">
              <h2 className="text-xl font-semibold text-gray-900">Message Queue Summary</h2>
            </div>
            <div className="p-6">
              <div className="space-y-4">
                <div className="flex justify-between items-center">
                  <span className="text-sm text-gray-600">Total Messages</span>
                  <span className="text-lg font-semibold">{queueSummary.total_messages.toLocaleString()}</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-sm text-gray-600">Pending</span>
                  <span className="text-lg font-semibold text-yellow-600">{queueSummary.pending_messages.toLocaleString()}</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-sm text-gray-600">Processing</span>
                  <span className="text-lg font-semibold text-blue-600">{queueSummary.processing_messages.toLocaleString()}</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-sm text-gray-600">Completed</span>
                  <span className="text-lg font-semibold text-green-600">{queueSummary.completed_messages.toLocaleString()}</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-sm text-gray-600">Failed</span>
                  <span className="text-lg font-semibold text-red-600">{queueSummary.failed_messages.toLocaleString()}</span>
                </div>
                <div className="pt-4 border-t">
                  <div className="flex justify-between items-center">
                    <span className="text-sm text-gray-600">High Priority Pending</span>
                    <span className="text-lg font-semibold text-orange-600">{queueSummary.high_priority_pending.toLocaleString()}</span>
                  </div>
                  <div className="flex justify-between items-center mt-2">
                    <span className="text-sm text-gray-600">Oldest Pending Age</span>
                    <span className="text-lg font-semibold">{Math.floor(queueSummary.oldest_pending_age / 60)}m</span>
                  </div>
                  <div className="flex justify-between items-center mt-2">
                    <span className="text-sm text-gray-600">Avg Processing Time</span>
                    <span className="text-lg font-semibold">{queueSummary.average_processing_time.toFixed(1)}s</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Action Buttons */}
      <div className="mt-6 flex gap-4">
        <button
          onClick={loadDashboardData}
          className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
        >
          Refresh Dashboard
        </button>
        <a
          href="/gold-lending/integration/providers"
          className="px-4 py-2 bg-gray-100 text-gray-700 rounded hover:bg-gray-200"
        >
          Manage Providers
        </a>
        <a
          href="/gold-lending/integration/monitoring"
          className="px-4 py-2 bg-gray-100 text-gray-700 rounded hover:bg-gray-200"
        >
          View Logs
        </a>
      </div>
    </div>
  );
}
