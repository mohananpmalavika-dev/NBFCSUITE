'use client';

import { useEffect, useState } from 'react';
import {
  getWebhooks,
  createWebhook,
  updateWebhook,
  deleteWebhook,
  testWebhook,
  getWebhookDeliveries,
  getIntegrationConfigurations,
  type Webhook,
  type IntegrationConfiguration,
  type WebhookDelivery,
} from '../../phase13_integration_api';

export default function WebhooksPage() {
  const [webhooks, setWebhooks] = useState<Webhook[]>([]);
  const [configurations, setConfigurations] = useState<IntegrationConfiguration[]>([]);
  const [deliveries, setDeliveries] = useState<{ [key: number]: WebhookDelivery[] }>({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showModal, setShowModal] = useState(false);
  const [showTestModal, setShowTestModal] = useState<number | null>(null);
  const [testPayload, setTestPayload] = useState('{"test": "data"}');
  const [editingWebhook, setEditingWebhook] = useState<Webhook | null>(null);
  const [expandedWebhook, setExpandedWebhook] = useState<number | null>(null);
  const [formData, setFormData] = useState({
    config_id: 0,
    webhook_url: '',
    event_type: '',
    secret_key: '',
    retry_policy: '{"max_attempts": 3, "backoff": "exponential"}',
    headers: '{}',
    is_active: true,
  });

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      setLoading(true);
      const [webhooksData, configsData] = await Promise.all([
        getWebhooks({ limit: 100 }),
        getIntegrationConfigurations({ limit: 100 }),
      ]);
      setWebhooks(webhooksData);
      setConfigurations(configsData);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load data');
    } finally {
      setLoading(false);
    }
  };

  const loadDeliveries = async (webhookId: number) => {
    try {
      const deliveriesData = await getWebhookDeliveries({ webhook_id: webhookId, limit: 10 });
      setDeliveries({ ...deliveries, [webhookId]: deliveriesData });
      setExpandedWebhook(expandedWebhook === webhookId ? null : webhookId);
    } catch (err) {
      alert('Failed to load deliveries');
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      JSON.parse(formData.retry_policy);
      JSON.parse(formData.headers);

      if (editingWebhook) {
        await updateWebhook(editingWebhook.webhook_id, formData);
      } else {
        await createWebhook(formData);
      }
      setShowModal(false);
      setEditingWebhook(null);
      resetForm();
      loadData();
    } catch (err) {
      alert(err instanceof Error ? err.message : 'Failed to save webhook');
    }
  };

  const handleTest = async () => {
    if (!showTestModal) return;
    try {
      const payload = JSON.parse(testPayload);
      const result = await testWebhook(showTestModal, payload);
      alert(`Test successful!\n${JSON.stringify(result, null, 2)}`);
      setShowTestModal(null);
    } catch (err) {
      alert(err instanceof Error ? err.message : 'Test failed');
    }
  };

  const handleDelete = async (webhookId: number) => {
    if (!confirm('Delete this webhook?')) return;
    try {
      await deleteWebhook(webhookId);
      loadData();
    } catch (err) {
      alert('Failed to delete webhook');
    }
  };

  const resetForm = () => {
    setFormData({
      config_id: 0,
      webhook_url: '',
      event_type: '',
      secret_key: '',
      retry_policy: '{"max_attempts": 3, "backoff": "exponential"}',
      headers: '{}',
      is_active: true,
    });
  };

  if (loading) {
    return <div className="flex items-center justify-center min-h-screen">
      <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
    </div>;
  }

  return (
    <div className="p-6 max-w-7xl mx-auto">
      <div className="mb-6 flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Webhooks</h1>
          <p className="text-gray-600 mt-2">Manage webhook subscriptions and deliveries</p>
        </div>
        <button onClick={() => { resetForm(); setShowModal(true); }}
          className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700">
          Add Webhook
        </button>
      </div>

      <div className="bg-white rounded-lg shadow overflow-hidden">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">URL</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Event Type</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Last Triggered</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Actions</th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {webhooks.map((webhook) => (
              <>
                <tr key={webhook.webhook_id} className="hover:bg-gray-50">
                  <td className="px-6 py-4">
                    <div className="text-sm text-gray-900">{webhook.webhook_url}</div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className="px-2 py-1 text-xs font-semibold rounded-full bg-purple-100 text-purple-800">
                      {webhook.event_type}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`px-2 py-1 text-xs font-semibold rounded-full ${
                      webhook.is_active ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'
                    }`}>
                      {webhook.is_active ? 'Active' : 'Inactive'}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {webhook.last_triggered ? new Date(webhook.last_triggered).toLocaleString() : 'Never'}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium space-x-2">
                    <button onClick={() => loadDeliveries(webhook.webhook_id)}
                      className="text-blue-600 hover:text-blue-900">
                      {expandedWebhook === webhook.webhook_id ? 'Hide' : 'History'}
                    </button>
                    <button onClick={() => setShowTestModal(webhook.webhook_id)}
                      className="text-purple-600 hover:text-purple-900">Test</button>
                    <button onClick={() => { setEditingWebhook(webhook); setFormData({
                      config_id: webhook.config_id, webhook_url: webhook.webhook_url,
                      event_type: webhook.event_type, secret_key: webhook.secret_key || '',
                      retry_policy: JSON.stringify(webhook.retry_policy, null, 2),
                      headers: JSON.stringify(webhook.headers || {}, null, 2),
                      is_active: webhook.is_active
                    }); setShowModal(true); }} className="text-blue-600 hover:text-blue-900">Edit</button>
                    <button onClick={() => handleDelete(webhook.webhook_id)}
                      className="text-red-600 hover:text-red-900">Delete</button>
                  </td>
                </tr>
                {expandedWebhook === webhook.webhook_id && (
                  <tr>
                    <td colSpan={5} className="px-6 py-4 bg-gray-50">
                      <h4 className="font-semibold mb-2">Recent Deliveries</h4>
                      {deliveries[webhook.webhook_id]?.length > 0 ? (
                        <div className="space-y-2">
                          {deliveries[webhook.webhook_id].map((d) => (
                            <div key={d.delivery_id} className="flex justify-between items-center text-sm border-b pb-2">
                              <span className={`px-2 py-1 rounded ${
                                d.status === 'success' ? 'bg-green-100 text-green-800' :
                                d.status === 'failure' ? 'bg-red-100 text-red-800' :
                                'bg-yellow-100 text-yellow-800'
                              }`}>{d.status}</span>
                              <span>{new Date(d.sent_at).toLocaleString()}</span>
                              <span>Retries: {d.retry_count}</span>
                              <span>{d.response_time}ms</span>
                            </div>
                          ))}
                        </div>
                      ) : <p className="text-gray-500">No deliveries yet</p>}
                    </td>
                  </tr>
                )}
              </>
            ))}
          </tbody>
        </table>
        {webhooks.length === 0 && (
          <div className="text-center py-12 text-gray-500">No webhooks found</div>
        )}
      </div>

      {showModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 max-w-2xl w-full max-h-[90vh] overflow-y-auto">
            <h2 className="text-2xl font-bold mb-4">{editingWebhook ? 'Edit' : 'Create'} Webhook</h2>
            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Configuration *</label>
                <select required value={formData.config_id}
                  onChange={(e) => setFormData({ ...formData, config_id: parseInt(e.target.value) })}
                  className="w-full px-3 py-2 border rounded">
                  <option value={0}>Select Configuration</option>
                  {configurations.map((c) => (
                    <option key={c.config_id} value={c.config_id}>{c.config_name}</option>
                  ))}
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Webhook URL *</label>
                <input type="url" required value={formData.webhook_url}
                  onChange={(e) => setFormData({ ...formData, webhook_url: e.target.value })}
                  className="w-full px-3 py-2 border rounded" placeholder="https://your-app.com/webhook"/>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Event Type *</label>
                <input type="text" required value={formData.event_type}
                  onChange={(e) => setFormData({ ...formData, event_type: e.target.value })}
                  className="w-full px-3 py-2 border rounded" placeholder="loan.approved"/>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Secret Key</label>
                <input type="password" value={formData.secret_key}
                  onChange={(e) => setFormData({ ...formData, secret_key: e.target.value })}
                  className="w-full px-3 py-2 border rounded"/>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Retry Policy (JSON)</label>
                <textarea value={formData.retry_policy}
                  onChange={(e) => setFormData({ ...formData, retry_policy: e.target.value })}
                  className="w-full px-3 py-2 border rounded font-mono text-sm" rows={3}/>
              </div>
              <div className="flex items-center">
                <input type="checkbox" checked={formData.is_active}
                  onChange={(e) => setFormData({ ...formData, is_active: e.target.checked })} className="mr-2"/>
                <label className="text-sm font-medium text-gray-700">Active</label>
              </div>
              <div className="flex justify-end gap-2 mt-6">
                <button type="button" onClick={() => { setShowModal(false); setEditingWebhook(null); }}
                  className="px-4 py-2 bg-gray-200 text-gray-700 rounded hover:bg-gray-300">Cancel</button>
                <button type="submit" className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700">
                  {editingWebhook ? 'Update' : 'Create'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {showTestModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 max-w-2xl w-full">
            <h3 className="text-lg font-bold mb-4">Test Webhook</h3>
            <textarea value={testPayload} onChange={(e) => setTestPayload(e.target.value)}
              className="w-full px-3 py-2 border rounded font-mono text-sm mb-4" rows={10}/>
            <div className="flex justify-end gap-2">
              <button onClick={() => setShowTestModal(null)}
                className="px-4 py-2 bg-gray-200 text-gray-700 rounded hover:bg-gray-300">Cancel</button>
              <button onClick={handleTest}
                className="px-4 py-2 bg-purple-600 text-white rounded hover:bg-purple-700">Send Test</button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
