'use client';

import { useEffect, useState } from 'react';
import {
  getIntegrationConfigurations,
  createIntegrationConfiguration,
  updateIntegrationConfiguration,
  deleteIntegrationConfiguration,
  approveIntegrationConfiguration,
  checkConfigurationHealth,
  getIntegrationProviders,
  type IntegrationConfiguration,
  type IntegrationProvider,
} from '../../phase13_integration_api';

export default function IntegrationConfigurationsPage() {
  const [configurations, setConfigurations] = useState<IntegrationConfiguration[]>([]);
  const [providers, setProviders] = useState<IntegrationProvider[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showModal, setShowModal] = useState(false);
  const [editingConfig, setEditingConfig] = useState<IntegrationConfiguration | null>(null);
  const [showApproveModal, setShowApproveModal] = useState<number | null>(null);
  const [approvedBy, setApprovedBy] = useState('');
  const [filterProvider, setFilterProvider] = useState<string>('');
  const [filterEnvironment, setFilterEnvironment] = useState<string>('');
  const [formData, setFormData] = useState({
    provider_id: 0,
    config_name: '',
    environment: 'development',
    base_url: '',
    auth_config: '{}',
    timeout_seconds: 30,
    retry_config: '{"max_retries": 3, "backoff_factor": 2}',
    rate_limit_config: '{}',
    status: 'pending',
    created_by: 1,
  });

  useEffect(() => {
    loadData();
  }, [filterProvider, filterEnvironment]);

  const loadData = async () => {
    try {
      setLoading(true);
      setError(null);
      const [configsData, providersData] = await Promise.all([
        getIntegrationConfigurations({
          limit: 100,
          provider_id: filterProvider ? parseInt(filterProvider) : undefined,
          environment: filterEnvironment || undefined,
        }),
        getIntegrationProviders({ limit: 100 }),
      ]);
      setConfigurations(configsData);
      setProviders(providersData);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load data');
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      // Validate JSON fields
      JSON.parse(formData.auth_config);
      JSON.parse(formData.retry_config);
      JSON.parse(formData.rate_limit_config);

      if (editingConfig) {
        await updateIntegrationConfiguration(editingConfig.config_id, formData);
      } else {
        await createIntegrationConfiguration(formData);
      }
      setShowModal(false);
      setEditingConfig(null);
      resetForm();
      loadData();
    } catch (err) {
      alert(err instanceof Error ? err.message : 'Failed to save configuration');
    }
  };

  const handleApprove = async () => {
    if (!showApproveModal || !approvedBy) return;
    try {
      await approveIntegrationConfiguration(showApproveModal, parseInt(approvedBy));
      setShowApproveModal(null);
      setApprovedBy('');
      loadData();
    } catch (err) {
      alert(err instanceof Error ? err.message : 'Failed to approve configuration');
    }
  };

  const handleHealthCheck = async (configId: number) => {
    try {
      const result = await checkConfigurationHealth(configId);
      alert(`Health check successful!\nStatus: ${result.status}\nLast check: ${result.last_check}`);
      loadData();
    } catch (err) {
      alert(err instanceof Error ? err.message : 'Health check failed');
    }
  };

  const handleDelete = async (configId: number) => {
    if (!confirm('Are you sure you want to delete this configuration?')) return;
    try {
      await deleteIntegrationConfiguration(configId);
      loadData();
    } catch (err) {
      alert(err instanceof Error ? err.message : 'Failed to delete configuration');
    }
  };

  const handleEdit = (config: IntegrationConfiguration) => {
    setEditingConfig(config);
    setFormData({
      provider_id: config.provider_id,
      config_name: config.config_name,
      environment: config.environment,
      base_url: config.base_url,
      auth_config: JSON.stringify(config.auth_config, null, 2),
      timeout_seconds: config.timeout_seconds,
      retry_config: JSON.stringify(config.retry_config, null, 2),
      rate_limit_config: JSON.stringify(config.rate_limit_config || {}, null, 2),
      status: config.status,
      created_by: config.created_by,
    });
    setShowModal(true);
  };

  const resetForm = () => {
    setFormData({
      provider_id: 0,
      config_name: '',
      environment: 'development',
      base_url: '',
      auth_config: '{}',
      timeout_seconds: 30,
      retry_config: '{"max_retries": 3, "backoff_factor": 2}',
      rate_limit_config: '{}',
      status: 'pending',
      created_by: 1,
    });
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading configurations...</p>
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
          <button onClick={loadData} className="mt-2 bg-red-600 text-white px-4 py-2 rounded hover:bg-red-700">
            Retry
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="p-6 max-w-7xl mx-auto">
      <div className="mb-6 flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Integration Configurations</h1>
          <p className="text-gray-600 mt-2">Manage integration connection settings</p>
        </div>
        <button
          onClick={() => {
            resetForm();
            setEditingConfig(null);
            setShowModal(true);
          }}
          className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
        >
          Add Configuration
        </button>
      </div>

      {/* Filters */}
      <div className="mb-4 flex gap-4">
        <select
          value={filterProvider}
          onChange={(e) => setFilterProvider(e.target.value)}
          className="px-4 py-2 border rounded"
        >
          <option value="">All Providers</option>
          {providers.map((p) => (
            <option key={p.provider_id} value={p.provider_id}>
              {p.provider_name}
            </option>
          ))}
        </select>
        <select
          value={filterEnvironment}
          onChange={(e) => setFilterEnvironment(e.target.value)}
          className="px-4 py-2 border rounded"
        >
          <option value="">All Environments</option>
          <option value="development">Development</option>
          <option value="staging">Staging</option>
          <option value="production">Production</option>
        </select>
      </div>

      {/* Configurations Table */}
      <div className="bg-white rounded-lg shadow overflow-hidden">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Name</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Provider</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Environment</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Health</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Actions</th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {configurations.map((config) => {
              const provider = providers.find((p) => p.provider_id === config.provider_id);
              return (
                <tr key={config.config_id} className="hover:bg-gray-50">
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm font-medium text-gray-900">{config.config_name}</div>
                    <div className="text-sm text-gray-500">{config.base_url}</div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {provider?.provider_name || `ID: ${config.provider_id}`}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`px-2 py-1 text-xs font-semibold rounded-full ${
                      config.environment === 'production' ? 'bg-red-100 text-red-800' :
                      config.environment === 'staging' ? 'bg-yellow-100 text-yellow-800' :
                      'bg-green-100 text-green-800'
                    }`}>
                      {config.environment}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`px-2 py-1 text-xs font-semibold rounded-full ${
                      config.status === 'active' ? 'bg-green-100 text-green-800' :
                      config.status === 'pending' ? 'bg-yellow-100 text-yellow-800' :
                      'bg-gray-100 text-gray-800'
                    }`}>
                      {config.status}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {config.last_health_check
                      ? new Date(config.last_health_check).toLocaleDateString()
                      : 'Never'}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium space-x-2">
                    <button
                      onClick={() => handleEdit(config)}
                      className="text-blue-600 hover:text-blue-900"
                    >
                      Edit
                    </button>
                    {config.status === 'pending' && (
                      <button
                        onClick={() => setShowApproveModal(config.config_id)}
                        className="text-green-600 hover:text-green-900"
                      >
                        Approve
                      </button>
                    )}
                    <button
                      onClick={() => handleHealthCheck(config.config_id)}
                      className="text-purple-600 hover:text-purple-900"
                    >
                      Health
                    </button>
                    <button
                      onClick={() => handleDelete(config.config_id)}
                      className="text-red-600 hover:text-red-900"
                    >
                      Delete
                    </button>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
        {configurations.length === 0 && (
          <div className="text-center py-12 text-gray-500">
            No configurations found. Create your first configuration to get started.
          </div>
        )}
      </div>

      {/* Create/Edit Modal */}
      {showModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 max-w-3xl w-full max-h-[90vh] overflow-y-auto">
            <h2 className="text-2xl font-bold mb-4">
              {editingConfig ? 'Edit Configuration' : 'Create Configuration'}
            </h2>
            <form onSubmit={handleSubmit} className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Provider *</label>
                  <select
                    required
                    value={formData.provider_id}
                    onChange={(e) => setFormData({ ...formData, provider_id: parseInt(e.target.value) })}
                    className="w-full px-3 py-2 border rounded"
                  >
                    <option value={0}>Select Provider</option>
                    {providers.map((p) => (
                      <option key={p.provider_id} value={p.provider_id}>
                        {p.provider_name}
                      </option>
                    ))}
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Environment *</label>
                  <select
                    value={formData.environment}
                    onChange={(e) => setFormData({ ...formData, environment: e.target.value })}
                    className="w-full px-3 py-2 border rounded"
                  >
                    <option value="development">Development</option>
                    <option value="staging">Staging</option>
                    <option value="production">Production</option>
                  </select>
                </div>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Configuration Name *</label>
                <input
                  type="text"
                  required
                  value={formData.config_name}
                  onChange={(e) => setFormData({ ...formData, config_name: e.target.value })}
                  className="w-full px-3 py-2 border rounded"
                  placeholder="e.g., Core Bank Production Config"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Base URL *</label>
                <input
                  type="url"
                  required
                  value={formData.base_url}
                  onChange={(e) => setFormData({ ...formData, base_url: e.target.value })}
                  className="w-full px-3 py-2 border rounded"
                  placeholder="https://api.example.com"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Auth Config (JSON) *</label>
                <textarea
                  required
                  value={formData.auth_config}
                  onChange={(e) => setFormData({ ...formData, auth_config: e.target.value })}
                  className="w-full px-3 py-2 border rounded font-mono text-sm"
                  rows={4}
                  placeholder='{"api_key": "your-key", "client_id": "your-id"}'
                />
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Timeout (seconds) *</label>
                  <input
                    type="number"
                    required
                    min="1"
                    value={formData.timeout_seconds}
                    onChange={(e) => setFormData({ ...formData, timeout_seconds: parseInt(e.target.value) })}
                    className="w-full px-3 py-2 border rounded"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Status *</label>
                  <select
                    value={formData.status}
                    onChange={(e) => setFormData({ ...formData, status: e.target.value })}
                    className="w-full px-3 py-2 border rounded"
                  >
                    <option value="pending">Pending</option>
                    <option value="active">Active</option>
                    <option value="inactive">Inactive</option>
                  </select>
                </div>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Retry Config (JSON)</label>
                <textarea
                  value={formData.retry_config}
                  onChange={(e) => setFormData({ ...formData, retry_config: e.target.value })}
                  className="w-full px-3 py-2 border rounded font-mono text-sm"
                  rows={3}
                  placeholder='{"max_retries": 3, "backoff_factor": 2}'
                />
              </div>
              <div className="flex justify-end gap-2 mt-6">
                <button
                  type="button"
                  onClick={() => {
                    setShowModal(false);
                    setEditingConfig(null);
                    resetForm();
                  }}
                  className="px-4 py-2 bg-gray-200 text-gray-700 rounded hover:bg-gray-300"
                >
                  Cancel
                </button>
                <button type="submit" className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700">
                  {editingConfig ? 'Update' : 'Create'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Approve Modal */}
      {showApproveModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 max-w-md w-full">
            <h3 className="text-lg font-bold mb-4">Approve Configuration</h3>
            <p className="text-gray-600 mb-4">Enter your user ID to approve this configuration:</p>
            <input
              type="number"
              value={approvedBy}
              onChange={(e) => setApprovedBy(e.target.value)}
              className="w-full px-3 py-2 border rounded mb-4"
              placeholder="Approver User ID"
            />
            <div className="flex justify-end gap-2">
              <button
                onClick={() => {
                  setShowApproveModal(null);
                  setApprovedBy('');
                }}
                className="px-4 py-2 bg-gray-200 text-gray-700 rounded hover:bg-gray-300"
              >
                Cancel
              </button>
              <button
                onClick={handleApprove}
                disabled={!approvedBy}
                className="px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700 disabled:opacity-50"
              >
                Approve
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
