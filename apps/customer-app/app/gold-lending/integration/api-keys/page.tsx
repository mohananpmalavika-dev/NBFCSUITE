'use client';

import { useEffect, useState } from 'react';
import {
  getAPIKeys,
  createAPIKey,
  revokeAPIKey,
  rotateAPIKey,
  getIntegrationConfigurations,
  type APIKey,
  type IntegrationConfiguration,
} from '../../phase13_integration_api';

export default function APIKeysPage() {
  const [keys, setKeys] = useState<APIKey[]>([]);
  const [configurations, setConfigurations] = useState<IntegrationConfiguration[]>([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [showViewModal, setShowViewModal] = useState<APIKey | null>(null);
  const [showRotateModal, setShowRotateModal] = useState<number | null>(null);
  const [newKeyValue, setNewKeyValue] = useState('');
  const [formData, setFormData] = useState({
    config_id: 0,
    key_name: '',
    key_value: '',
    key_prefix: 'sk_',
    permissions: '{}',
    expires_at: '',
    created_by: 1,
  });

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      setLoading(true);
      const [keysData, configsData] = await Promise.all([
        getAPIKeys({ limit: 100 }),
        getIntegrationConfigurations({ limit: 100 }),
      ]);
      setKeys(keysData);
      setConfigurations(configsData);
    } catch (err) {
      alert('Failed to load data');
    } finally {
      setLoading(false);
    }
  };

  const generateKey = () => {
    const env = configurations.find(c => c.config_id === formData.config_id)?.environment || 'dev';
    const random = Math.random().toString(36).substring(2, 15) + Math.random().toString(36).substring(2, 15);
    const key = `sk_${env}_${random}`;
    setFormData({ ...formData, key_value: key, key_prefix: `sk_${env}_` });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      JSON.parse(formData.permissions);
      const createdKey = await createAPIKey(formData);
      setShowModal(false);
      setShowViewModal(createdKey);
      resetForm();
      loadData();
    } catch (err) {
      alert(err instanceof Error ? err.message : 'Failed to create API key');
    }
  };

  const handleRevoke = async (keyId: number) => {
    if (!confirm('Revoke this API key? This cannot be undone.')) return;
    try {
      await revokeAPIKey(keyId);
      loadData();
    } catch (err) {
      alert('Failed to revoke key');
    }
  };

  const handleRotate = async () => {
    if (!showRotateModal || !newKeyValue) return;
    try {
      await rotateAPIKey(showRotateModal, newKeyValue);
      setShowRotateModal(null);
      setNewKeyValue('');
      loadData();
      alert('API key rotated successfully!');
    } catch (err) {
      alert('Failed to rotate key');
    }
  };

  const maskKey = (key: string, prefix?: string) => {
    if (prefix && key.startsWith(prefix)) {
      return prefix + '•'.repeat(20);
    }
    return key.substring(0, 8) + '•'.repeat(20);
  };

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text);
    alert('Copied to clipboard!');
  };

  const resetForm = () => {
    setFormData({
      config_id: 0,
      key_name: '',
      key_value: '',
      key_prefix: 'sk_',
      permissions: '{}',
      expires_at: '',
      created_by: 1,
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
          <h1 className="text-3xl font-bold text-gray-900">API Keys</h1>
          <p className="text-gray-600 mt-2">Manage API keys for integrations</p>
        </div>
        <button onClick={() => { resetForm(); setShowModal(true); }}
          className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700">
          Create API Key
        </button>
      </div>

      <div className="bg-white rounded-lg shadow overflow-hidden">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Name</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Key</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Expires</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Last Used</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Actions</th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {keys.map((key) => (
              <tr key={key.key_id} className="hover:bg-gray-50">
                <td className="px-6 py-4">
                  <div className="text-sm font-medium text-gray-900">{key.key_name}</div>
                  <div className="text-sm text-gray-500">
                    {configurations.find(c => c.config_id === key.config_id)?.config_name || `Config ${key.config_id}`}
                  </div>
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <span className="font-mono text-sm text-gray-600">{maskKey(key.key_value, key.key_prefix)}</span>
                  <button onClick={() => copyToClipboard(key.key_value)}
                    className="ml-2 text-blue-600 hover:text-blue-900 text-xs">Copy</button>
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  {key.expires_at ? new Date(key.expires_at).toLocaleDateString() : 'Never'}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  {key.last_used_at ? new Date(key.last_used_at).toLocaleDateString() : 'Never'}
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <span className={`px-2 py-1 text-xs font-semibold rounded-full ${
                    key.is_active ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                  }`}>
                    {key.is_active ? 'Active' : 'Revoked'}
                  </span>
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm font-medium space-x-2">
                  {key.is_active && (
                    <>
                      <button onClick={() => setShowRotateModal(key.key_id)}
                        className="text-purple-600 hover:text-purple-900">Rotate</button>
                      <button onClick={() => handleRevoke(key.key_id)}
                        className="text-red-600 hover:text-red-900">Revoke</button>
                    </>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
        {keys.length === 0 && (
          <div className="text-center py-12 text-gray-500">No API keys found</div>
        )}
      </div>

      {showModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 max-w-2xl w-full">
            <h2 className="text-2xl font-bold mb-4">Create API Key</h2>
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
                <label className="block text-sm font-medium text-gray-700 mb-1">Key Name *</label>
                <input type="text" required value={formData.key_name}
                  onChange={(e) => setFormData({ ...formData, key_name: e.target.value })}
                  className="w-full px-3 py-2 border rounded" placeholder="Production API Key"/>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Key Value *</label>
                <div className="flex gap-2">
                  <input type="text" required value={formData.key_value}
                    onChange={(e) => setFormData({ ...formData, key_value: e.target.value })}
                    className="flex-1 px-3 py-2 border rounded font-mono text-sm"/>
                  <button type="button" onClick={generateKey}
                    className="px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700">Generate</button>
                </div>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Permissions (JSON)</label>
                <textarea value={formData.permissions}
                  onChange={(e) => setFormData({ ...formData, permissions: e.target.value })}
                  className="w-full px-3 py-2 border rounded font-mono text-sm" rows={3}
                  placeholder='{"read": true, "write": true}'/>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Expires At (optional)</label>
                <input type="date" value={formData.expires_at}
                  onChange={(e) => setFormData({ ...formData, expires_at: e.target.value })}
                  className="w-full px-3 py-2 border rounded"/>
              </div>
              <div className="flex justify-end gap-2 mt-6">
                <button type="button" onClick={() => setShowModal(false)}
                  className="px-4 py-2 bg-gray-200 text-gray-700 rounded hover:bg-gray-300">Cancel</button>
                <button type="submit"
                  className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700">Create</button>
              </div>
            </form>
          </div>
        </div>
      )}

      {showViewModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 max-w-2xl w-full">
            <h3 className="text-lg font-bold mb-4 text-green-600">API Key Created Successfully!</h3>
            <div className="bg-yellow-50 border border-yellow-200 p-4 rounded mb-4">
              <p className="text-sm text-yellow-800 font-semibold mb-2">
                ⚠️ Save this key securely. You won't be able to see it again!
              </p>
            </div>
            <div className="bg-gray-50 p-4 rounded mb-4">
              <label className="block text-sm font-medium text-gray-700 mb-2">API Key:</label>
              <div className="flex items-center gap-2">
                <code className="flex-1 px-3 py-2 bg-white border rounded font-mono text-sm break-all">
                  {showViewModal.key_value}
                </code>
                <button onClick={() => copyToClipboard(showViewModal.key_value)}
                  className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700">Copy</button>
              </div>
            </div>
            <div className="flex justify-end">
              <button onClick={() => setShowViewModal(null)}
                className="px-4 py-2 bg-gray-600 text-white rounded hover:bg-gray-700">Close</button>
            </div>
          </div>
        </div>
      )}

      {showRotateModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 max-w-md w-full">
            <h3 className="text-lg font-bold mb-4">Rotate API Key</h3>
            <p className="text-gray-600 mb-4">Enter the new key value:</p>
            <input type="text" value={newKeyValue} onChange={(e) => setNewKeyValue(e.target.value)}
              className="w-full px-3 py-2 border rounded mb-4 font-mono text-sm"
              placeholder="sk_prod_new_key_value"/>
            <div className="flex justify-end gap-2">
              <button onClick={() => { setShowRotateModal(null); setNewKeyValue(''); }}
                className="px-4 py-2 bg-gray-200 text-gray-700 rounded hover:bg-gray-300">Cancel</button>
              <button onClick={handleRotate} disabled={!newKeyValue}
                className="px-4 py-2 bg-purple-600 text-white rounded hover:bg-purple-700 disabled:opacity-50">
                Rotate
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
