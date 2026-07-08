'use client';

import { useState, useEffect } from 'react';
import { useRouter, useParams } from 'next/navigation';
import { fieldAgentApi } from '@/lib/api/collection';
import { FieldAgent } from '@/types/collection';
import { CollectionStatCard } from '@/components/collections';

export default function FieldAgentDetailPage() {
  const router = useRouter();
  const params = useParams();
  const agentId = params.id as string;

  const [agent, setAgent] = useState<FieldAgent | null>(null);
  const [loading, setLoading] = useState(true);
  const [stats, setStats] = useState({
    totalCases: 0,
    completedVisits: 0,
    pendingVisits: 0,
    collectionAmount: 0,
    successRate: 0,
  });
  const [recentVisits, setRecentVisits] = useState<any[]>([]);

  useEffect(() => {
    loadAgentDetails();
  }, [agentId]);

  const loadAgentDetails = async () => {
    try {
      setLoading(true);
      const data = await fieldAgentApi.getAgent(parseInt(agentId));
      setAgent(data);
      
      // Load agent statistics
      // This would come from API in real implementation
      setStats({
        totalCases: 45,
        completedVisits: 120,
        pendingVisits: 15,
        collectionAmount: 2850000,
        successRate: 68,
      });

      // Load recent visits
      setRecentVisits([
        {
          id: '1',
          loan_account_id: 'LA-2024-001',
          customer_name: 'Rajesh Kumar',
          visit_date: '2024-01-15',
          disposition: 'payment_collected',
          amount: 15000,
        },
        {
          id: '2',
          loan_account_id: 'LA-2024-002',
          customer_name: 'Priya Sharma',
          visit_date: '2024-01-14',
          disposition: 'customer_met',
          amount: 0,
        },
      ]);
    } catch (error) {
      console.error('Failed to load agent details:', error);
    } finally {
      setLoading(false);
    }
  };

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR',
      maximumFractionDigits: 0,
    }).format(amount);
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-IN', {
      day: '2-digit',
      month: 'short',
      year: 'numeric',
    });
  };

  const getStatusColor = (status: string) => {
    const colors: Record<string, string> = {
      active: 'bg-green-100 text-green-800',
      inactive: 'bg-gray-100 text-gray-800',
      on_leave: 'bg-yellow-100 text-yellow-800',
      suspended: 'bg-red-100 text-red-800',
    };
    return colors[status] || 'bg-gray-100 text-gray-800';
  };

  const getDispositionColor = (disposition: string) => {
    const colors: Record<string, string> = {
      payment_collected: 'bg-green-100 text-green-800',
      promise_to_pay: 'bg-blue-100 text-blue-800',
      customer_met: 'bg-yellow-100 text-yellow-800',
      customer_not_available: 'bg-gray-100 text-gray-800',
      wrong_address: 'bg-red-100 text-red-800',
      refused_to_pay: 'bg-red-100 text-red-800',
    };
    return colors[disposition] || 'bg-gray-100 text-gray-800';
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-gray-500">Loading agent details...</div>
      </div>
    );
  }

  if (!agent) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <p className="text-gray-500 mb-4">Agent not found</p>
          <button
            onClick={() => router.push('/collections/field-agents')}
            className="text-blue-600 hover:text-blue-700"
          >
            Back to Field Agents
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex justify-between items-start">
        <div>
          <button
            onClick={() => router.push('/collections/field-agents')}
            className="text-blue-600 hover:text-blue-700 mb-2 flex items-center gap-1"
          >
            ← Back to Field Agents
          </button>
          <h1 className="text-2xl font-bold text-gray-900">{agent.name}</h1>
          <p className="text-gray-600 mt-1">{agent.employee_id}</p>
        </div>
        <div className="flex gap-3">
          <span className={`px-4 py-2 rounded-lg text-sm font-medium ${getStatusColor(agent.status)}`}>
            {agent.status.toUpperCase()}
          </span>
          <button
            onClick={() => router.push(`/collections/field-agents/${agent.id}/edit`)}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
          >
            Edit Agent
          </button>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
        <CollectionStatCard
          title="Total Cases"
          value={stats.totalCases.toString()}
          icon="📋"
        />
        <CollectionStatCard
          title="Completed Visits"
          value={stats.completedVisits.toString()}
          icon="✅"
          trend="success"
        />
        <CollectionStatCard
          title="Pending Visits"
          value={stats.pendingVisits.toString()}
          icon="⏳"
          trend="warning"
        />
        <CollectionStatCard
          title="Collections"
          value={formatCurrency(stats.collectionAmount)}
          icon="💰"
          trend="success"
        />
        <CollectionStatCard
          title="Success Rate"
          value={`${stats.successRate}%`}
          icon="📈"
          trend={stats.successRate >= 70 ? 'success' : 'warning'}
        />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Main Content - Left Side */}
        <div className="lg:col-span-2 space-y-6">
          {/* Agent Information */}
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Agent Information</h2>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <p className="text-sm text-gray-600">Employee ID</p>
                <p className="font-medium text-gray-900">{agent.employee_id}</p>
              </div>
              <div>
                <p className="text-sm text-gray-600">Name</p>
                <p className="font-medium text-gray-900">{agent.name}</p>
              </div>
              <div>
                <p className="text-sm text-gray-600">Mobile</p>
                <p className="font-medium text-gray-900">{agent.mobile}</p>
              </div>
              <div>
                <p className="text-sm text-gray-600">Email</p>
                <p className="font-medium text-gray-900">{agent.email || 'N/A'}</p>
              </div>
              <div>
                <p className="text-sm text-gray-600">Status</p>
                <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getStatusColor(agent.status)}`}>
                  {agent.status.toUpperCase()}
                </span>
              </div>
              <div>
                <p className="text-sm text-gray-600">Max Cases</p>
                <p className="font-medium text-gray-900">{agent.max_cases}</p>
              </div>
              <div>
                <p className="text-sm text-gray-600">Joined Date</p>
                <p className="font-medium text-gray-900">{formatDate(agent.created_at)}</p>
              </div>
              {agent.reporting_to && (
                <div>
                  <p className="text-sm text-gray-600">Reports To</p>
                  <p className="font-medium text-gray-900">{agent.reporting_to}</p>
                </div>
              )}
            </div>
          </div>

          {/* Territory Information */}
          {agent.territories && agent.territories.length > 0 && (
            <div className="bg-white rounded-lg shadow p-6">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">Assigned Territories</h2>
              <div className="space-y-3">
                {agent.territories.map((territory, index) => (
                  <div key={index} className="p-4 bg-gray-50 rounded-lg">
                    <div className="flex justify-between items-start">
                      <div>
                        <p className="font-medium text-gray-900">{territory.name}</p>
                        {territory.description && (
                          <p className="text-sm text-gray-600 mt-1">{territory.description}</p>
                        )}
                        <div className="flex gap-4 mt-2">
                          {territory.pincodes && (
                            <p className="text-xs text-gray-500">
                              Pincodes: {territory.pincodes.join(', ')}
                            </p>
                          )}
                        </div>
                      </div>
                      <span className={`px-2.5 py-0.5 rounded-full text-xs font-medium ${territory.is_active ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'}`}>
                        {territory.is_active ? 'Active' : 'Inactive'}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Recent Visits */}
          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-lg font-semibold text-gray-900">Recent Visits</h2>
              <button
                onClick={() => router.push(`/collections/field-agents/${agent.id}/visits`)}
                className="text-blue-600 hover:text-blue-700 text-sm font-medium"
              >
                View All →
              </button>
            </div>
            {recentVisits.length === 0 ? (
              <div className="text-center py-8 text-gray-500">No visits recorded yet</div>
            ) : (
              <div className="space-y-3">
                {recentVisits.map((visit) => (
                  <div key={visit.id} className="p-4 bg-gray-50 rounded-lg">
                    <div className="flex justify-between items-start">
                      <div className="flex-1">
                        <div className="flex items-center gap-3 mb-2">
                          <p className="font-medium text-gray-900">{visit.customer_name}</p>
                          <span className="text-sm text-gray-600">{visit.loan_account_id}</span>
                        </div>
                        <div className="flex items-center gap-3">
                          <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getDispositionColor(visit.disposition)}`}>
                            {visit.disposition.replace('_', ' ').toUpperCase()}
                          </span>
                          <span className="text-sm text-gray-600">{formatDate(visit.visit_date)}</span>
                          {visit.amount > 0 && (
                            <span className="text-sm font-medium text-green-600">
                              {formatCurrency(visit.amount)}
                            </span>
                          )}
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* Sidebar - Right Side */}
        <div className="space-y-6">
          {/* Quick Actions */}
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Quick Actions</h2>
            <div className="space-y-2">
              <button
                onClick={() => router.push(`/collections/field-agents/${agent.id}/assign-cases`)}
                className="w-full px-4 py-2 bg-blue-50 text-blue-700 rounded-lg hover:bg-blue-100 text-left"
              >
                📋 Assign Cases
              </button>
              <button
                onClick={() => router.push(`/collections/field-agents/${agent.id}/visits`)}
                className="w-full px-4 py-2 bg-purple-50 text-purple-700 rounded-lg hover:bg-purple-100 text-left"
              >
                🚗 View All Visits
              </button>
              <button
                onClick={() => router.push(`/collections/field-agents/${agent.id}/performance`)}
                className="w-full px-4 py-2 bg-green-50 text-green-700 rounded-lg hover:bg-green-100 text-left"
              >
                📊 Performance Report
              </button>
              <button
                onClick={() => router.push(`/collections/field-agents/${agent.id}/edit`)}
                className="w-full px-4 py-2 bg-gray-50 text-gray-700 rounded-lg hover:bg-gray-100 text-left"
              >
                ✏️ Edit Profile
              </button>
            </div>
          </div>

          {/* Performance Metrics */}
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">This Month</h2>
            <div className="space-y-4">
              <div>
                <div className="flex justify-between items-center mb-1">
                  <span className="text-sm text-gray-600">Collection Target</span>
                  <span className="text-sm font-medium text-gray-900">75%</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div className="bg-green-600 h-2 rounded-full" style={{ width: '75%' }}></div>
                </div>
                <p className="text-xs text-gray-500 mt-1">
                  ₹21.37L / ₹28.50L
                </p>
              </div>
              <div>
                <div className="flex justify-between items-center mb-1">
                  <span className="text-sm text-gray-600">Visit Target</span>
                  <span className="text-sm font-medium text-gray-900">80%</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div className="bg-blue-600 h-2 rounded-full" style={{ width: '80%' }}></div>
                </div>
                <p className="text-xs text-gray-500 mt-1">
                  24 / 30 visits
                </p>
              </div>
              <div>
                <div className="flex justify-between items-center mb-1">
                  <span className="text-sm text-gray-600">Success Rate</span>
                  <span className="text-sm font-medium text-gray-900">{stats.successRate}%</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div className="bg-purple-600 h-2 rounded-full" style={{ width: `${stats.successRate}%` }}></div>
                </div>
              </div>
            </div>
          </div>

          {/* Contact Information */}
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Contact</h2>
            <div className="space-y-3">
              <div className="flex items-center gap-3">
                <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center">
                  📱
                </div>
                <div>
                  <p className="text-xs text-gray-600">Mobile</p>
                  <p className="font-medium text-gray-900">{agent.mobile}</p>
                </div>
              </div>
              {agent.email && (
                <div className="flex items-center gap-3">
                  <div className="w-8 h-8 bg-purple-100 rounded-full flex items-center justify-center">
                    ✉️
                  </div>
                  <div>
                    <p className="text-xs text-gray-600">Email</p>
                    <p className="font-medium text-gray-900 text-sm break-all">{agent.email}</p>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
