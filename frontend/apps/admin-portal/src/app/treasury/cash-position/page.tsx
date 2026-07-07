'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { treasuryService, CashPositionStatistics, CashAlert } from '@/services/treasury.service';

export default function CashPositionPage() {
  const router = useRouter();
  const [loading, setLoading] = useState(true);
  const [statistics, setStatistics] = useState<CashPositionStatistics | null>(null);
  const [alerts, setAlerts] = useState<CashAlert[]>([]);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      setLoading(true);
      const [statsData, alertsData] = await Promise.all([
        treasuryService.getCashStatistics(),
        treasuryService.getCashAlerts()
      ]);
      setStatistics(statsData);
      setAlerts(alertsData);
      setError(null);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to load cash position data');
    } finally {
      setLoading(false);
    }
  };

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0
    }).format(amount);
  };

  const getAlertColor = (severity: string) => {
    switch (severity) {
      case 'critical': return 'bg-red-50 border-red-200 text-red-800';
      case 'warning': return 'bg-yellow-50 border-yellow-200 text-yellow-800';
      case 'info': return 'bg-blue-50 border-blue-200 text-blue-800';
      default: return 'bg-gray-50 border-gray-200 text-gray-800';
    }
  };

  if (loading) {
    return (
      <div className="p-6">
        <div className="flex items-center justify-center h-64">
          <div className="text-gray-600">Loading cash position...</div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-6">
        <div className="bg-red-50 border border-red-200 text-red-800 px-4 py-3 rounded-lg">
          {error}
        </div>
        <button
          onClick={loadData}
          className="mt-4 px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-lg hover:bg-blue-700"
        >
          Retry
        </button>
      </div>
    );
  }

  return (
    <div className="p-6">
      {/* Header */}
      <div className="mb-6 flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Cash Position Management</h1>
          <p className="text-sm text-gray-600 mt-1">Real-time cash position across all branches</p>
        </div>
        <div className="flex space-x-3">
          <button
            onClick={() => router.push('/treasury/cash-position/record')}
            className="px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-lg hover:bg-blue-700"
          >
            Record Cash Position
          </button>
          <button
            onClick={() => router.push('/treasury/cash-position/list')}
            className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50"
          >
            View All Positions
          </button>
        </div>
      </div>

      {/* Statistics Cards */}
      {statistics && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
          <div className="bg-white border border-gray-200 rounded-lg p-4">
            <div className="text-sm text-gray-600 mb-1">Total Cash on Hand</div>
            <div className="text-2xl font-bold text-gray-900">
              {formatCurrency(statistics.total_cash_on_hand)}
            </div>
            <div className="text-xs text-gray-500 mt-1">Across all branches</div>
          </div>

          <div className="bg-white border border-gray-200 rounded-lg p-4">
            <div className="text-sm text-gray-600 mb-1">Total Branches</div>
            <div className="text-2xl font-bold text-gray-900">{statistics.total_branches}</div>
            <div className="text-xs text-gray-500 mt-1">
              {statistics.branches_with_low_cash} with low cash
            </div>
          </div>

          <div className="bg-white border border-gray-200 rounded-lg p-4">
            <div className="text-sm text-gray-600 mb-1">Cash Received Today</div>
            <div className="text-2xl font-bold text-green-600">
              {formatCurrency(statistics.total_cash_received_today)}
            </div>
            <div className="text-xs text-gray-500 mt-1">Total collections</div>
          </div>

          <div className="bg-white border border-gray-200 rounded-lg p-4">
            <div className="text-sm text-gray-600 mb-1">Bank Deposits Today</div>
            <div className="text-2xl font-bold text-blue-600">
              {formatCurrency(statistics.total_bank_deposits_today)}
            </div>
            <div className="text-xs text-gray-500 mt-1">Deposited to banks</div>
          </div>
        </div>
      )}

      {/* Alerts Section */}
      {alerts.length > 0 && (
        <div className="mb-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-3">Active Alerts</h2>
          <div className="space-y-2">
            {alerts.map((alert, index) => (
              <div
                key={index}
                className={`border rounded-lg p-4 ${getAlertColor(alert.severity)}`}
              >
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center space-x-2">
                      <span className="text-sm font-medium capitalize">{alert.alert_type.replace('_', ' ')}</span>
                      {alert.branch_name && (
                        <span className="text-xs px-2 py-1 bg-white bg-opacity-50 rounded">
                          {alert.branch_name}
                        </span>
                      )}
                    </div>
                    <p className="text-sm mt-1">{alert.message}</p>
                  </div>
                  <span className={`text-xs px-2 py-1 rounded ${
                    alert.severity === 'critical' ? 'bg-red-200' :
                    alert.severity === 'warning' ? 'bg-yellow-200' : 'bg-blue-200'
                  }`}>
                    {alert.severity}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Quick Actions */}
      <div className="mb-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-3">Quick Actions</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <button
            onClick={() => router.push('/treasury/cash-position/record')}
            className="bg-white border border-gray-200 rounded-lg p-4 text-left hover:border-blue-300 hover:shadow-sm transition-all"
          >
            <div className="flex items-center space-x-3">
              <div className="p-2 bg-blue-100 rounded-lg">
                <svg className="w-6 h-6 text-blue-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
                </svg>
              </div>
              <div>
                <h3 className="text-sm font-medium text-gray-900">Record Cash Position</h3>
                <p className="text-xs text-gray-600 mt-1">Enter today's cash details</p>
              </div>
            </div>
          </button>

          <button
            onClick={() => router.push('/treasury/cash-position/list')}
            className="bg-white border border-gray-200 rounded-lg p-4 text-left hover:border-blue-300 hover:shadow-sm transition-all"
          >
            <div className="flex items-center space-x-3">
              <div className="p-2 bg-green-100 rounded-lg">
                <svg className="w-6 h-6 text-green-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
                </svg>
              </div>
              <div>
                <h3 className="text-sm font-medium text-gray-900">View All Positions</h3>
                <p className="text-xs text-gray-600 mt-1">Browse historical data</p>
              </div>
            </div>
          </button>

          <button
            onClick={() => router.push('/treasury/cash-position/reports')}
            className="bg-white border border-gray-200 rounded-lg p-4 text-left hover:border-blue-300 hover:shadow-sm transition-all"
          >
            <div className="flex items-center space-x-3">
              <div className="p-2 bg-purple-100 rounded-lg">
                <svg className="w-6 h-6 text-purple-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                </svg>
              </div>
              <div>
                <h3 className="text-sm font-medium text-gray-900">Cash Reports</h3>
                <p className="text-xs text-gray-600 mt-1">Movement and trends</p>
              </div>
            </div>
          </button>
        </div>
      </div>

      {/* Recent Positions (Placeholder) */}
      <div className="bg-white shadow rounded-lg p-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">Recent Cash Positions</h2>
        <div className="text-sm text-gray-500 italic">
          Recent cash positions will be displayed here. Use the "View All Positions" button to see the complete list.
        </div>
      </div>
    </div>
  );
}
