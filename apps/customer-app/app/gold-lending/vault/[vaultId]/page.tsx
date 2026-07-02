'use client';

import { useParams } from 'next/navigation';
import { useEffect, useState } from 'react';
import { goldApi } from '../../goldApi';
import Link from 'next/link';

interface VaultHierarchy {
  vault: any;
  racks: any[];
  total_capacity: number;
  current_occupancy: number;
  occupancy_percentage: number;
}

export default function VaultDetailPage() {
  const params = useParams();
  const vaultId = params.vaultId as string;
  
  const [hierarchy, setHierarchy] = useState<VaultHierarchy | null>(null);
  const [packets, setPackets] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState('hierarchy');

  useEffect(() => {
    if (vaultId) {
      loadVaultData();
    }
  }, [vaultId]);

  const loadVaultData = async () => {
    try {
      setLoading(true);
      setError(null);
      const [hierarchyData, packetsData] = await Promise.all([
        goldApi.getVaultHierarchy(vaultId),
        goldApi.listPackets({ vault_id: vaultId })
      ]);
      setHierarchy(hierarchyData);
      setPackets(packetsData);
    } catch (err: any) {
      setError(err.message || 'Failed to load vault data');
      console.error('Error loading vault data:', err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading vault details...</p>
        </div>
      </div>
    );
  }

  if (error || !hierarchy) {
    return (
      <div className="p-6">
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <h2 className="text-red-800 font-semibold mb-2">Error Loading Vault</h2>
          <p className="text-red-600">{error || 'Vault not found'}</p>
        </div>
      </div>
    );
  }

  const vault = hierarchy.vault;

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b">
        <div className="max-w-7xl mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div>
              <div className="flex items-center gap-3 mb-2">
                <Link
                  href="/gold-lending/vault"
                  className="text-gray-600 hover:text-gray-900"
                >
                  ← Back to Vaults
                </Link>
              </div>
              <h1 className="text-2xl font-bold text-gray-900">{vault.vault_name}</h1>
              <p className="text-sm text-gray-500 mt-1">
                {vault.vault_code} • {vault.branch_id}
              </p>
            </div>
            <div className="flex gap-3">
              <span className={`px-3 py-1 rounded-full text-sm font-medium ${
                vault.security_level === 'high' ? 'bg-red-100 text-red-800' :
                vault.security_level === 'medium' ? 'bg-yellow-100 text-yellow-800' :
                'bg-blue-100 text-blue-800'
              }`}>
                {vault.security_level.toUpperCase()} Security
              </span>
              <span className={`px-3 py-1 rounded-full text-sm font-medium ${
                vault.is_active ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'
              }`}>
                {vault.is_active ? 'Active' : 'Inactive'}
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* Stats */}
      <div className="max-w-7xl mx-auto px-6 py-6">
        <div className="grid grid-cols-1 md:grid-cols-5 gap-4 mb-6">
          <div className="bg-white rounded-lg shadow p-4">
            <div className="text-sm text-gray-600 mb-1">Total Capacity</div>
            <div className="text-2xl font-bold text-gray-900">{hierarchy.total_capacity}</div>
            <div className="text-xs text-gray-500 mt-1">packets</div>
          </div>
          <div className="bg-white rounded-lg shadow p-4">
            <div className="text-sm text-gray-600 mb-1">Current Occupancy</div>
            <div className="text-2xl font-bold text-gray-900">{hierarchy.current_occupancy}</div>
            <div className="text-xs text-gray-500 mt-1">packets stored</div>
          </div>
          <div className="bg-white rounded-lg shadow p-4">
            <div className="text-sm text-gray-600 mb-1">Occupancy Rate</div>
            <div className="text-2xl font-bold text-gray-900">{hierarchy.occupancy_percentage.toFixed(1)}%</div>
            <div className="text-xs text-gray-500 mt-1">capacity used</div>
          </div>
          <div className="bg-white rounded-lg shadow p-4">
            <div className="text-sm text-gray-600 mb-1">Racks</div>
            <div className="text-2xl font-bold text-gray-900">{hierarchy.racks.length}</div>
            <div className="text-xs text-gray-500 mt-1">
              {hierarchy.racks.reduce((sum, r) => sum + r.lockers.length, 0)} lockers
            </div>
          </div>
          <div className="bg-white rounded-lg shadow p-4">
            <div className="text-sm text-gray-600 mb-1">Available Space</div>
            <div className="text-2xl font-bold text-gray-900">
              {hierarchy.total_capacity - hierarchy.current_occupancy}
            </div>
            <div className="text-xs text-gray-500 mt-1">packets free</div>
          </div>
        </div>

        {/* Tabs */}
        <div className="bg-white rounded-lg shadow">
          <div className="border-b">
            <nav className="flex -mb-px">
              {[
                { id: 'hierarchy', label: 'Vault Hierarchy' },
                { id: 'packets', label: `Packets (${packets.length})` },
                { id: 'activity', label: 'Activity Log' },
              ].map((tab) => (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`px-6 py-3 text-sm font-medium border-b-2 ${
                    activeTab === tab.id
                      ? 'border-blue-600 text-blue-600'
                      : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                  }`}
                >
                  {tab.label}
                </button>
              ))}
            </nav>
          </div>

          <div className="p-6">
            {activeTab === 'hierarchy' && (
              <HierarchyTab hierarchy={hierarchy} />
            )}
            {activeTab === 'packets' && (
              <PacketsTab packets={packets} />
            )}
            {activeTab === 'activity' && (
              <ActivityTab vaultId={vaultId} />
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

function HierarchyTab({ hierarchy }: { hierarchy: VaultHierarchy }) {
  if (hierarchy.racks.length === 0) {
    return (
      <div className="text-center py-12 text-gray-500">
        <p className="mb-4">No racks configured in this vault</p>
        <button className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700">
          + Add Rack
        </button>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {hierarchy.racks.map((rack: any) => (
        <div key={rack.id} className="border rounded-lg p-4">
          <div className="flex items-center justify-between mb-3">
            <div>
              <h4 className="font-semibold text-lg">Rack {rack.rack_code}</h4>
              <p className="text-sm text-gray-600">
                {rack.current_occupancy}/{rack.capacity_lockers} lockers occupied
              </p>
            </div>
            <button className="text-blue-600 hover:text-blue-800 text-sm">
              View Details →
            </button>
          </div>

          {/* Lockers Grid */}
          {rack.lockers && rack.lockers.length > 0 && (
            <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mt-3">
              {rack.lockers.map((locker: any) => (
                <div
                  key={locker.id}
                  className={`p-3 rounded border-2 ${
                    locker.current_occupancy >= locker.capacity_trays
                      ? 'border-red-300 bg-red-50'
                      : locker.current_occupancy > 0
                      ? 'border-yellow-300 bg-yellow-50'
                      : 'border-green-300 bg-green-50'
                  }`}
                >
                  <div className="font-medium text-sm">{locker.locker_code}</div>
                  <div className="text-xs text-gray-600">
                    {locker.current_occupancy}/{locker.capacity_trays} trays
                  </div>
                  <div className="text-xs text-gray-500 mt-1">
                    {locker.lock_type}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      ))}
    </div>
  );
}

function PacketsTab({ packets }: { packets: any[] }) {
  if (packets.length === 0) {
    return (
      <div className="text-center py-12 text-gray-500">
        No packets currently stored in this vault
      </div>
    );
  }

  return (
    <div className="space-y-3">
      {packets.map((packet: any) => (
        <Link
          key={packet.id}
          href={`/gold-lending/vault/packets/${packet.id}`}
          className="block border rounded-lg p-4 hover:shadow-md transition-shadow"
        >
          <div className="flex justify-between items-start">
            <div>
              <h4 className="font-semibold">{packet.packet_number}</h4>
              <p className="text-sm text-gray-600 mt-1">
                Customer: {packet.customer_id}
              </p>
              <p className="text-xs text-gray-500 mt-1">
                {packet.total_ornaments} ornaments • {packet.total_weight_grams}g • ₹{packet.total_value?.toLocaleString()}
              </p>
            </div>
            <div className="text-right">
              <span className={`px-2 py-1 text-xs rounded-full ${
                packet.seal_status === 'intact' ? 'bg-green-100 text-green-800' :
                packet.seal_status === 'broken' ? 'bg-red-100 text-red-800' :
                'bg-yellow-100 text-yellow-800'
              }`}>
                {packet.seal_status || 'No Seal'}
              </span>
              <p className="text-xs text-gray-500 mt-2">{packet.seal_number}</p>
            </div>
          </div>
        </Link>
      ))}
    </div>
  );
}

function ActivityTab({ vaultId }: { vaultId: string }) {
  const [accessLogs, setAccessLogs] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadAccessLogs();
  }, [vaultId]);

  const loadAccessLogs = async () => {
    try {
      const data = await goldApi.listVaultAccess(vaultId, {});
      setAccessLogs(data);
    } catch (err) {
      console.error('Error loading access logs:', err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <div className="text-center py-8">Loading activity...</div>;
  }

  if (accessLogs.length === 0) {
    return (
      <div className="text-center py-12 text-gray-500">
        No access activity recorded
      </div>
    );
  }

  return (
    <div className="space-y-3">
      {accessLogs.map((log: any) => (
        <div key={log.id} className="border rounded-lg p-4">
          <div className="flex justify-between items-start">
            <div>
              <div className="font-medium">{log.access_type}</div>
              <div className="text-sm text-gray-600 mt-1">User: {log.user_id}</div>
              {log.purpose && (
                <div className="text-sm text-gray-500 mt-1">{log.purpose}</div>
              )}
            </div>
            <div className="text-right text-sm">
              <div className="text-gray-900">
                {new Date(log.access_timestamp).toLocaleString()}
              </div>
              {log.duration_minutes && (
                <div className="text-gray-600 mt-1">
                  {log.duration_minutes} minutes
                </div>
              )}
            </div>
          </div>
        </div>
      ))}
    </div>
  );
}
