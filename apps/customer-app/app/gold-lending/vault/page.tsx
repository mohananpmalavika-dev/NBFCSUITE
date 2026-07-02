'use client';

import { useEffect, useState } from 'react';
import { goldApi } from '../goldApi';
import Link from 'next/link';

interface Vault {
  id: string;
  vault_code: string;
  vault_name: string;
  branch_id: string;
  vault_type: string;
  security_level: string;
  capacity_packets: number;
  current_occupancy: number;
  occupancy_percentage: number;
  is_active: boolean;
  temperature_controlled: boolean;
  humidity_controlled: boolean;
}

export default function VaultManagementPage() {
  const [vaults, setVaults] = useState<Vault[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedBranch, setSelectedBranch] = useState<string>('all');
  const [showCreateModal, setShowCreateModal] = useState(false);

  useEffect(() => {
    loadVaults();
  }, [selectedBranch]);

  const loadVaults = async () => {
    try {
      setLoading(true);
      setError(null);
      const params = selectedBranch !== 'all' ? { branch_id: selectedBranch } : {};
      const data = await goldApi.listVaults(params);
      setVaults(data);
    } catch (err: any) {
      setError(err.message || 'Failed to load vaults');
      console.error('Error loading vaults:', err);
    } finally {
      setLoading(false);
    }
  };

  const getOccupancyColor = (percentage: number) => {
    if (percentage >= 90) return 'text-red-600 bg-red-100';
    if (percentage >= 75) return 'text-orange-600 bg-orange-100';
    if (percentage >= 50) return 'text-yellow-600 bg-yellow-100';
    return 'text-green-600 bg-green-100';
  };

  const getSecurityBadge = (level: string) => {
    const colors = {
      high: 'bg-red-100 text-red-800',
      medium: 'bg-yellow-100 text-yellow-800',
      standard: 'bg-blue-100 text-blue-800'
    };
    return colors[level as keyof typeof colors] || 'bg-gray-100 text-gray-800';
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading vaults...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b">
        <div className="max-w-7xl mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-gray-900">Vault Management</h1>
              <p className="text-sm text-gray-500 mt-1">
                Manage vaults, packets, and security seals
              </p>
            </div>
            <div className="flex gap-3">
              <button
                onClick={() => setShowCreateModal(true)}
                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
              >
                + Create Vault
              </button>
              <Link
                href="/gold-lending/vault/packets"
                className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700"
              >
                View Packets
              </Link>
            </div>
          </div>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="max-w-7xl mx-auto px-6 py-6">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
          <div className="bg-white rounded-lg shadow p-4">
            <div className="text-sm text-gray-600 mb-1">Total Vaults</div>
            <div className="text-2xl font-bold text-gray-900">{vaults.length}</div>
            <div className="text-xs text-green-600 mt-1">
              {vaults.filter(v => v.is_active).length} active
            </div>
          </div>
          <div className="bg-white rounded-lg shadow p-4">
            <div className="text-sm text-gray-600 mb-1">Total Capacity</div>
            <div className="text-2xl font-bold text-gray-900">
              {vaults.reduce((sum, v) => sum + v.capacity_packets, 0)}
            </div>
            <div className="text-xs text-gray-500 mt-1">packets</div>
          </div>
          <div className="bg-white rounded-lg shadow p-4">
            <div className="text-sm text-gray-600 mb-1">Current Occupancy</div>
            <div className="text-2xl font-bold text-gray-900">
              {vaults.reduce((sum, v) => sum + v.current_occupancy, 0)}
            </div>
            <div className="text-xs text-gray-500 mt-1">packets stored</div>
          </div>
          <div className="bg-white rounded-lg shadow p-4">
            <div className="text-sm text-gray-600 mb-1">Avg Occupancy</div>
            <div className="text-2xl font-bold text-gray-900">
              {vaults.length > 0 
                ? Math.round(vaults.reduce((sum, v) => sum + (v.occupancy_percentage || 0), 0) / vaults.length)
                : 0}%
            </div>
            <div className="text-xs text-gray-500 mt-1">across all vaults</div>
          </div>
        </div>

        {/* Error Display */}
        {error && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-6">
            <p className="text-red-800">{error}</p>
          </div>
        )}

        {/* Vaults Grid */}
        {vaults.length === 0 ? (
          <div className="bg-white rounded-lg shadow p-12 text-center">
            <div className="text-gray-400 mb-4">
              <svg className="w-16 h-16 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
              </svg>
            </div>
            <h3 className="text-lg font-semibold text-gray-900 mb-2">No Vaults Found</h3>
            <p className="text-gray-600 mb-4">Create your first vault to start managing gold packets</p>
            <button
              onClick={() => setShowCreateModal(true)}
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
            >
              Create Vault
            </button>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {vaults.map((vault) => (
              <Link
                key={vault.id}
                href={`/gold-lending/vault/${vault.id}`}
                className="block bg-white rounded-lg shadow hover:shadow-lg transition-shadow"
              >
                <div className="p-6">
                  {/* Header */}
                  <div className="flex items-start justify-between mb-4">
                    <div className="flex-1">
                      <h3 className="text-lg font-semibold text-gray-900 mb-1">
                        {vault.vault_name}
                      </h3>
                      <p className="text-sm text-gray-600">{vault.vault_code}</p>
                    </div>
                    {vault.is_active ? (
                      <span className="px-2 py-1 bg-green-100 text-green-800 text-xs rounded-full">
                        Active
                      </span>
                    ) : (
                      <span className="px-2 py-1 bg-gray-100 text-gray-800 text-xs rounded-full">
                        Inactive
                      </span>
                    )}
                  </div>

                  {/* Security & Type Badges */}
                  <div className="flex gap-2 mb-4">
                    <span className={`px-2 py-1 text-xs rounded ${getSecurityBadge(vault.security_level)}`}>
                      {vault.security_level.toUpperCase()}
                    </span>
                    <span className="px-2 py-1 bg-purple-100 text-purple-800 text-xs rounded">
                      {vault.vault_type}
                    </span>
                  </div>

                  {/* Features */}
                  <div className="flex gap-3 mb-4 text-xs text-gray-600">
                    {vault.temperature_controlled && (
                      <span className="flex items-center gap-1">
                        🌡️ Temp Ctrl
                      </span>
                    )}
                    {vault.humidity_controlled && (
                      <span className="flex items-center gap-1">
                        💧 Humidity Ctrl
                      </span>
                    )}
                  </div>

                  {/* Capacity Bar */}
                  <div className="mb-2">
                    <div className="flex justify-between text-sm mb-1">
                      <span className="text-gray-600">Occupancy</span>
                      <span className={`font-semibold ${getOccupancyColor(vault.occupancy_percentage || 0).split(' ')[0]}`}>
                        {vault.occupancy_percentage?.toFixed(1) || 0}%
                      </span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-2">
                      <div
                        className={`h-2 rounded-full transition-all ${
                          (vault.occupancy_percentage || 0) >= 90 ? 'bg-red-600' :
                          (vault.occupancy_percentage || 0) >= 75 ? 'bg-orange-600' :
                          (vault.occupancy_percentage || 0) >= 50 ? 'bg-yellow-600' :
                          'bg-green-600'
                        }`}
                        style={{ width: `${vault.occupancy_percentage || 0}%` }}
                      ></div>
                    </div>
                  </div>

                  {/* Stats */}
                  <div className="grid grid-cols-2 gap-4 pt-4 border-t">
                    <div>
                      <div className="text-xs text-gray-600">Capacity</div>
                      <div className="text-lg font-semibold text-gray-900">
                        {vault.capacity_packets}
                      </div>
                    </div>
                    <div>
                      <div className="text-xs text-gray-600">Occupied</div>
                      <div className="text-lg font-semibold text-gray-900">
                        {vault.current_occupancy}
                      </div>
                    </div>
                  </div>
                </div>
              </Link>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
