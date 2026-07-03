'use client';

import { useEffect, useState } from 'react';
import { goldApi } from '../../goldApi';

export default function ConcentrationRiskPage() {
  const [limits, setLimits] = useState<any[]>([]);
  const [monitoring, setMonitoring] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      setLoading(true);
      const [limitsData, monitorData] = await Promise.all([
        goldApi.listConcentrationRiskLimits({ is_active: true }),
        goldApi.monitorConcentrationRisks()
      ]);
      setLimits(limitsData);
      setMonitoring(monitorData);
    } catch (err) {
      console.error('Failed to load data:', err);
    } finally {
      setLoading(false);
    }
  };

  const getBreachColor = (status: string) => {
    switch (status) {
      case 'breached': return 'bg-red-100 text-red-800';
      case 'warning': return 'bg-yellow-100 text-yellow-800';
      case 'within_limit': return 'bg-green-100 text-green-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getUtilizationColor = (percentage: number) => {
    if (percentage >= 100) return 'bg-red-500';
    if (percentage >= 80) return 'bg-yellow-500';
    return 'bg-green-500';
  };

  return (
    <div className="p-6 space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Concentration Risk Limits</h1>
          <p className="text-gray-600 mt-1">Monitor concentration risk across portfolio segments</p>
        </div>
        <button className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700">
          New Limit
        </button>
      </div>

      {/* Monitoring Dashboard */}
      <div className="bg-white rounded-lg shadow">
        <div className="px-6 py-4 border-b border-gray-200">
          <h2 className="text-lg font-semibold text-gray-900">Real-time Monitoring</h2>
        </div>
        <div className="p-6">
          {loading ? (
            <div className="text-center py-8"><div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div></div>
          ) : (
            <div className="space-y-4">
              {monitoring.map((item) => (
                <div key={item.limit_id} className="border border-gray-200 rounded-lg p-4">
                  <div className="flex items-center justify-between mb-2">
                    <div>
                      <h3 className="font-semibold text-gray-900">{item.limit_name}</h3>
                      <p className="text-sm text-gray-600">{item.concentration_type}</p>
                    </div>
                    <span className={`px-3 py-1 rounded-full text-sm font-medium ${getBreachColor(item.breach_status)}`}>
                      {item.breach_status}
                    </span>
                  </div>
                  <div className="mt-3">
                    <div className="flex justify-between text-sm mb-1">
                      <span className="text-gray-600">Utilization</span>
                      <span className="font-medium">{item.utilization_percentage?.toFixed(2)}%</span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-3">
                      <div
                        className={`h-3 rounded-full ${getUtilizationColor(item.utilization_percentage)}`}
                        style={{ width: `${Math.min(item.utilization_percentage, 100)}%` }}
                      ></div>
                    </div>
                    <div className="flex justify-between text-xs text-gray-500 mt-1">
                      <span>Current: ${(item.current_utilization || 0).toLocaleString()}</span>
                      <span>Limit: ${(item.limit_amount || 0).toLocaleString()}</span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Limits Configuration */}
      <div className="bg-white rounded-lg shadow overflow-hidden">
        <div className="px-6 py-4 border-b border-gray-200">
          <h2 className="text-lg font-semibold text-gray-900">Configured Limits</h2>
        </div>
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Limit Name</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Type</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Limit Amount</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Warning %</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {limits.map((limit) => (
              <tr key={limit.limit_id} className="hover:bg-gray-50">
                <td className="px-6 py-4 text-sm font-medium">{limit.limit_name}</td>
                <td className="px-6 py-4 text-sm">{limit.concentration_type}</td>
                <td className="px-6 py-4 text-sm">${(limit.limit_amount || 0).toLocaleString()}</td>
                <td className="px-6 py-4 text-sm">{limit.warning_threshold}%</td>
                <td className="px-6 py-4 text-sm">
                  <span className={`px-2 py-1 rounded-full text-xs ${limit.is_active ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'}`}>
                    {limit.is_active ? 'Active' : 'Inactive'}
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
