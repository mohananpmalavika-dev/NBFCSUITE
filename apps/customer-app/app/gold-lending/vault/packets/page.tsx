'use client';

import { useEffect, useState } from 'react';
import { goldApi } from '../../goldApi';
import Link from 'next/link';

interface Packet {
  id: string;
  packet_number: string;
  customer_id: string;
  branch_id: string;
  current_location_type: string;
  total_ornaments: number;
  total_weight_grams: number;
  total_value: number;
  qr_code: string;
  seal_number: string;
  seal_status: string;
  packet_status: string;
  created_at: string;
}

export default function PacketsPage() {
  const [packets, setPackets] = useState<Packet[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [statusFilter, setStatusFilter] = useState<string>('all');
  const [searchTerm, setSearchTerm] = useState('');

  useEffect(() => {
    loadPackets();
  }, [statusFilter]);

  const loadPackets = async () => {
    try {
      setLoading(true);
      setError(null);
      const params = statusFilter !== 'all' ? { packet_status: statusFilter } : {};
      const data = await goldApi.listPackets(params);
      setPackets(data);
    } catch (err: any) {
      setError(err.message || 'Failed to load packets');
      console.error('Error loading packets:', err);
    } finally {
      setLoading(false);
    }
  };

  const filteredPackets = packets.filter(packet =>
    packet.packet_number.toLowerCase().includes(searchTerm.toLowerCase()) ||
    packet.customer_id.toLowerCase().includes(searchTerm.toLowerCase()) ||
    packet.seal_number?.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const getStatusColor = (status: string) => {
    const colors: Record<string, string> = {
      created: 'bg-gray-100 text-gray-800',
      sealed: 'bg-blue-100 text-blue-800',
      vaulted: 'bg-green-100 text-green-800',
      in_transit: 'bg-yellow-100 text-yellow-800',
      released: 'bg-purple-100 text-purple-800',
      auctioned: 'bg-red-100 text-red-800',
    };
    return colors[status] || 'bg-gray-100 text-gray-800';
  };

  const getSealStatusColor = (status: string) => {
    const colors: Record<string, string> = {
      intact: 'bg-green-100 text-green-800',
      broken: 'bg-red-100 text-red-800',
      tampered: 'bg-orange-100 text-orange-800',
      missing: 'bg-gray-100 text-gray-800',
    };
    return colors[status] || 'bg-gray-100 text-gray-800';
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading packets...</p>
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
              <h1 className="text-2xl font-bold text-gray-900">Packet Management</h1>
              <p className="text-sm text-gray-500 mt-1">
                Track and manage gold packets with QR codes
              </p>
            </div>
            <div className="flex gap-3">
              <Link
                href="/gold-lending/vault"
                className="px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700"
              >
                View Vaults
              </Link>
              <button className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700">
                + Create Packet
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Stats & Filters */}
      <div className="max-w-7xl mx-auto px-6 py-6">
        {/* Stats */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
          <div className="bg-white rounded-lg shadow p-4">
            <div className="text-sm text-gray-600 mb-1">Total Packets</div>
            <div className="text-2xl font-bold text-gray-900">{packets.length}</div>
          </div>
          <div className="bg-white rounded-lg shadow p-4">
            <div className="text-sm text-gray-600 mb-1">Vaulted</div>
            <div className="text-2xl font-bold text-green-600">
              {packets.filter(p => p.packet_status === 'vaulted').length}
            </div>
          </div>
          <div className="bg-white rounded-lg shadow p-4">
            <div className="text-sm text-gray-600 mb-1">In Transit</div>
            <div className="text-2xl font-bold text-yellow-600">
              {packets.filter(p => p.packet_status === 'in_transit').length}
            </div>
          </div>
          <div className="bg-white rounded-lg shadow p-4">
            <div className="text-sm text-gray-600 mb-1">Total Value</div>
            <div className="text-2xl font-bold text-gray-900">
              ₹{packets.reduce((sum, p) => sum + (p.total_value || 0), 0).toLocaleString()}
            </div>
          </div>
        </div>

        {/* Filters */}
        <div className="bg-white rounded-lg shadow p-4 mb-6">
          <div className="flex flex-col md:flex-row gap-4">
            {/* Search */}
            <div className="flex-1">
              <input
                type="text"
                placeholder="Search by packet number, customer ID, or seal number..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              />
            </div>

            {/* Status Filter */}
            <select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
              className="px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            >
              <option value="all">All Status</option>
              <option value="created">Created</option>
              <option value="sealed">Sealed</option>
              <option value="vaulted">Vaulted</option>
              <option value="in_transit">In Transit</option>
              <option value="released">Released</option>
            </select>
          </div>
        </div>

        {/* Error Display */}
        {error && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-6">
            <p className="text-red-800">{error}</p>
          </div>
        )}

        {/* Packets List */}
        {filteredPackets.length === 0 ? (
          <div className="bg-white rounded-lg shadow p-12 text-center">
            <div className="text-gray-400 mb-4">
              <svg className="w-16 h-16 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4" />
              </svg>
            </div>
            <h3 className="text-lg font-semibold text-gray-900 mb-2">No Packets Found</h3>
            <p className="text-gray-600">
              {searchTerm ? 'Try adjusting your search criteria' : 'Create your first packet to start managing gold ornaments'}
            </p>
          </div>
        ) : (
          <div className="bg-white rounded-lg shadow overflow-hidden">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Packet
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Customer
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Contents
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Location
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Seal
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Status
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Actions
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {filteredPackets.map((packet) => (
                  <tr key={packet.id} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm font-medium text-gray-900">{packet.packet_number}</div>
                      <div className="text-xs text-gray-500">{packet.qr_code}</div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm text-gray-900">{packet.customer_id}</div>
                      <div className="text-xs text-gray-500">{packet.branch_id}</div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm text-gray-900">{packet.total_ornaments} items</div>
                      <div className="text-xs text-gray-500">
                        {packet.total_weight_grams}g • ₹{packet.total_value?.toLocaleString()}
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className="text-sm text-gray-900">{packet.current_location_type}</span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      {packet.seal_number ? (
                        <>
                          <div className="text-sm text-gray-900">{packet.seal_number}</div>
                          <span className={`inline-block px-2 py-1 text-xs rounded-full mt-1 ${getSealStatusColor(packet.seal_status)}`}>
                            {packet.seal_status}
                          </span>
                        </>
                      ) : (
                        <span className="text-xs text-gray-500">No seal</span>
                      )}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`px-2 py-1 text-xs rounded-full ${getStatusColor(packet.packet_status)}`}>
                        {packet.packet_status}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm">
                      <Link
                        href={`/gold-lending/vault/packets/${packet.id}`}
                        className="text-blue-600 hover:text-blue-800"
                      >
                        View Details →
                      </Link>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
