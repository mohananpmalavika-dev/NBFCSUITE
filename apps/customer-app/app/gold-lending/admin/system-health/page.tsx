'use client';

import { useEffect, useState } from 'react';
import { phase15AdminAPI, SystemHealth } from '../../phase15_admin_api';

export default function SystemHealthPage() {
  const [healthChecks, setHealthChecks] = useState<SystemHealth[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadHealthChecks();
    const interval = setInterval(loadHealthChecks, 30000); // Refresh every 30 seconds
    return () => clearInterval(interval);
  }, []);

  const loadHealthChecks = async () => {
    try {
      setLoading(true);
      const data = await phase15AdminAPI.listHealthChecks({ limit: 100 });
      setHealthChecks(data);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const runCheck = async (id: string) => {
    try {
      await phase15AdminAPI.runHealthCheck(id);
      loadHealthChecks();
    } catch (err: any) {
      alert(`Error running health check: ${err.message}`);
    }
  };

  if (loading && healthChecks.length === 0) {
    return <div className="flex items-center justify-center min-h-screen"><div>Loading...</div></div>;
  }

  if (error) {
    return <div className="flex items-center justify-center min-h-screen"><div className="text-red-600">Error: {error}</div></div>;
  }

  const healthyCount = healthChecks.filter(h => h.health_status === 'HEALTHY').length;
  const unhealthyCount = healthChecks.filter(h => h.health_status === 'UNHEALTHY').length;
  const degradedCount = healthChecks.filter(h => h.health_status === 'DEGRADED').length;

  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold mb-8">System Health Monitoring</h1>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-gray-500 text-sm font-medium">Total Checks</h3>
          <p className="text-3xl font-bold text-blue-600">{healthChecks.length}</p>
        </div>
        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-gray-500 text-sm font-medium">Healthy</h3>
          <p className="text-3xl font-bold text-green-600">{healthyCount}</p>
        </div>
        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-gray-500 text-sm font-medium">Degraded</h3>
          <p className="text-3xl font-bold text-yellow-600">{degradedCount}</p>
        </div>
        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-gray-500 text-sm font-medium">Unhealthy</h3>
          <p className="text-3xl font-bold text-red-600">{unhealthyCount}</p>
        </div>
      </div>

      {/* Health Checks Table */}
      <div className="bg-white shadow rounded-lg overflow-hidden">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Component</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Response Time</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Availability</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Last Check</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Failures</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Actions</th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {healthChecks.map((check) => (
              <tr key={check.id} className="hover:bg-gray-50">
                <td className="px-6 py-4 whitespace-nowrap">
                  <div className="text-sm font-medium text-gray-900">{check.check_name}</div>
                  <div className="text-sm text-gray-500">{check.component_name}</div>
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${
                    check.health_status === 'HEALTHY' ? 'bg-green-100 text-green-800' :
                    check.health_status === 'DEGRADED' ? 'bg-yellow-100 text-yellow-800' :
                    'bg-red-100 text-red-800'
                  }`}>
                    {check.health_status}
                  </span>
                  {check.is_critical && <span className="ml-2 text-xs text-red-600">CRITICAL</span>}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  {check.response_time_ms ? `${check.response_time_ms}ms` : 'N/A'}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  {check.availability_percent ? `${check.availability_percent}%` : 'N/A'}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  {new Date(check.last_check_at).toLocaleString()}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  {check.consecutive_failures}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                  <button
                    onClick={() => runCheck(check.id)}
                    className="text-blue-600 hover:text-blue-900"
                  >
                    Run Check
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
