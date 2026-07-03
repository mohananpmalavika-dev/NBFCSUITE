'use client';

import { useEffect, useState } from 'react';
import { phase15AdminAPI, AdminOverview } from '../../phase15_admin_api';

export default function AdminDashboardPage() {
  const [overview, setOverview] = useState<AdminOverview | null>(null);
  const [healthMetrics, setHealthMetrics] = useState<any[]>([]);
  const [securityMetrics, setSecurityMetrics] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    try {
      setLoading(true);
      const [overviewData, healthData, securityData] = await Promise.all([
        phase15AdminAPI.getAdminOverview(),
        phase15AdminAPI.getSystemHealthMetrics({ limit: 5 }),
        phase15AdminAPI.getSecurityMetrics(),
      ]);
      setOverview(overviewData);
      setHealthMetrics(healthData);
      setSecurityMetrics(securityData);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-lg">Loading admin dashboard...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-red-600">Error: {error}</div>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold mb-8">Platform Administration Dashboard</h1>

      {/* Overview Stats */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-gray-500 text-sm font-medium">Total Users</h3>
          <p className="text-3xl font-bold text-blue-600">{overview?.total_users || 0}</p>
          <p className="text-sm text-gray-600 mt-1">{overview?.active_users || 0} active</p>
        </div>

        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-gray-500 text-sm font-medium">Roles & Permissions</h3>
          <p className="text-3xl font-bold text-green-600">{overview?.total_roles || 0}</p>
          <p className="text-sm text-gray-600 mt-1">{overview?.total_permissions || 0} permissions</p>
        </div>

        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-gray-500 text-sm font-medium">System Health</h3>
          <p className="text-3xl font-bold text-purple-600">{overview?.healthy_components || 0}/{overview?.total_system_health_checks || 0}</p>
          <p className="text-sm text-gray-600 mt-1">Healthy components</p>
        </div>

        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-gray-500 text-sm font-medium">Scheduled Jobs</h3>
          <p className="text-3xl font-bold text-orange-600">{overview?.active_scheduled_jobs || 0}/{overview?.total_scheduled_jobs || 0}</p>
          <p className="text-sm text-gray-600 mt-1">Active jobs</p>
        </div>
      </div>

      {/* Security Metrics */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
        <div className="bg-white p-6 rounded-lg shadow">
          <h2 className="text-xl font-semibold mb-4">Security Overview</h2>
          <div className="space-y-3">
            <div className="flex justify-between items-center">
              <span className="text-gray-600">Logins Today</span>
              <span className="font-semibold">{securityMetrics?.total_logins_today || 0}</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-gray-600">Failed Logins</span>
              <span className="font-semibold text-red-600">{securityMetrics?.failed_logins_today || 0}</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-gray-600">Suspicious Logins</span>
              <span className="font-semibold text-yellow-600">{securityMetrics?.suspicious_logins_today || 0}</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-gray-600">Active API Keys</span>
              <span className="font-semibold">{securityMetrics?.api_key_usage_count || 0}</span>
            </div>
          </div>
        </div>


        <div className="bg-white p-6 rounded-lg shadow">
          <h2 className="text-xl font-semibold mb-4">Feature Flags & Configuration</h2>
          <div className="space-y-3">
            <div className="flex justify-between items-center">
              <span className="text-gray-600">Total Feature Flags</span>
              <span className="font-semibold">{overview?.total_feature_flags || 0}</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-gray-600">Enabled Flags</span>
              <span className="font-semibold text-green-600">{overview?.enabled_feature_flags || 0}</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-gray-600">Total API Keys</span>
              <span className="font-semibold">{overview?.total_api_keys || 0}</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-gray-600">Audit Logs</span>
              <span className="font-semibold">{overview?.total_audit_logs || 0}</span>
            </div>
          </div>
        </div>
      </div>

      {/* System Health Status */}
      <div className="bg-white p-6 rounded-lg shadow mb-8">
        <h2 className="text-xl font-semibold mb-4">System Health Status</h2>
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Component</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Response Time</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Last Check</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Failures</th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {healthMetrics.map((metric: any, index: number) => (
                <tr key={index}>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                    {metric.component_name}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${
                      metric.health_status === 'HEALTHY' ? 'bg-green-100 text-green-800' :
                      metric.health_status === 'DEGRADED' ? 'bg-yellow-100 text-yellow-800' :
                      'bg-red-100 text-red-800'
                    }`}>
                      {metric.health_status}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {metric.response_time_ms ? `${metric.response_time_ms}ms` : 'N/A'}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {new Date(metric.last_check_at).toLocaleString()}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {metric.consecutive_failures}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Quick Actions */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <a href="/gold-lending/admin/users-roles" className="bg-blue-50 p-6 rounded-lg shadow hover:bg-blue-100 transition">
          <h3 className="text-lg font-semibold text-blue-900 mb-2">Manage Users & Roles</h3>
          <p className="text-sm text-blue-700">Configure user permissions and role assignments</p>
        </a>

        <a href="/gold-lending/admin/system-health" className="bg-green-50 p-6 rounded-lg shadow hover:bg-green-100 transition">
          <h3 className="text-lg font-semibold text-green-900 mb-2">System Health</h3>
          <p className="text-sm text-green-700">Monitor system components and performance</p>
        </a>

        <a href="/gold-lending/admin/audit-logs" className="bg-purple-50 p-6 rounded-lg shadow hover:bg-purple-100 transition">
          <h3 className="text-lg font-semibold text-purple-900 mb-2">Audit Logs</h3>
          <p className="text-sm text-purple-700">Review system activity and security events</p>
        </a>
      </div>
    </div>
  );
}
