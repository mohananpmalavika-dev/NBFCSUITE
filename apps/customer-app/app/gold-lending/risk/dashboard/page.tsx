'use client';

import { useEffect, useState } from 'react';
import { goldApi } from '../../goldApi';

export default function RiskDashboardPage() {
  const [loading, setLoading] = useState(true);
  const [creditStats, setCreditStats] = useState<any>(null);
  const [operationalStats, setOperationalStats] = useState<any>(null);
  const [marketStats, setMarketStats] = useState<any>(null);
  const [concentrationStats, setConcentrationStats] = useState<any>(null);
  const [complianceStats, setComplianceStats] = useState<any>(null);
  const [recentAlerts, setRecentAlerts] = useState<any[]>([]);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    try {
      setLoading(true);
      setError(null);

      const [credit, operational, market, concentration, compliance, alerts] = await Promise.all([
        goldApi.getCreditRiskStatistics(),
        goldApi.getOperationalRiskStatistics(),
        goldApi.getMarketRiskStatistics(),
        goldApi.getConcentrationRiskStatistics(),
        goldApi.getComplianceStatistics(),
        goldApi.listRiskAlerts({ alert_status: 'active', limit: 10 })
      ]);

      setCreditStats(credit);
      setOperationalStats(operational);
      setMarketStats(market);
      setConcentrationStats(concentration);
      setComplianceStats(compliance);
      setRecentAlerts(alerts);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load dashboard data');
    } finally {
      setLoading(false);
    }
  };

  const getSeverityColor = (severity: string) => {
    switch (severity?.toLowerCase()) {
      case 'critical': return 'bg-red-100 text-red-800';
      case 'high': return 'bg-orange-100 text-orange-800';
      case 'medium': return 'bg-yellow-100 text-yellow-800';
      case 'low': return 'bg-green-100 text-green-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  if (loading) {
    return (
      <div className="p-6">
        <div className="animate-pulse space-y-4">
          <div className="h-8 bg-gray-200 rounded w-1/4"></div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            {[1, 2, 3, 4].map(i => (
              <div key={i} className="h-32 bg-gray-200 rounded"></div>
            ))}
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-6">
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <h3 className="text-red-800 font-semibold">Error Loading Dashboard</h3>
          <p className="text-red-600 text-sm mt-1">{error}</p>
          <button
            onClick={loadDashboardData}
            className="mt-3 px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700"
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Risk Management Dashboard</h1>
          <p className="text-gray-600 mt-1">Comprehensive risk monitoring and analytics</p>
        </div>
        <button
          onClick={loadDashboardData}
          className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
        >
          Refresh Data
        </button>
      </div>

      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
        {/* Credit Risk */}
        <div className="bg-white rounded-lg shadow p-4 border-l-4 border-blue-500">
          <div className="text-sm text-gray-600">Credit Risk</div>
          <div className="text-2xl font-bold text-gray-900 mt-2">
            {creditStats?.total_assessments || 0}
          </div>
          <div className="text-xs text-gray-500 mt-1">Total Assessments</div>
          <div className="mt-3 text-sm">
            <span className="text-blue-600 font-medium">
              Avg Score: {creditStats?.average_risk_score?.toFixed(2) || 'N/A'}
            </span>
          </div>
        </div>

        {/* Operational Risk */}
        <div className="bg-white rounded-lg shadow p-4 border-l-4 border-orange-500">
          <div className="text-sm text-gray-600">Operational Risk</div>
          <div className="text-2xl font-bold text-gray-900 mt-2">
            {operationalStats?.total_events || 0}
          </div>
          <div className="text-xs text-gray-500 mt-1">Total Events</div>
          <div className="mt-3 text-sm">
            <span className="text-orange-600 font-medium">
              Loss: ${(operationalStats?.total_loss_amount || 0).toLocaleString()}
            </span>
          </div>
        </div>

        {/* Market Risk */}
        <div className="bg-white rounded-lg shadow p-4 border-l-4 border-purple-500">
          <div className="text-sm text-gray-600">Market Risk</div>
          <div className="text-2xl font-bold text-gray-900 mt-2">
            {marketStats?.total_exposures || 0}
          </div>
          <div className="text-xs text-gray-500 mt-1">Total Exposures</div>
          <div className="mt-3 text-sm">
            <span className="text-purple-600 font-medium">
              VaR: ${(marketStats?.total_var_amount || 0).toLocaleString()}
            </span>
          </div>
        </div>

        {/* Concentration Risk */}
        <div className="bg-white rounded-lg shadow p-4 border-l-4 border-yellow-500">
          <div className="text-sm text-gray-600">Concentration Risk</div>
          <div className="text-2xl font-bold text-gray-900 mt-2">
            {concentrationStats?.breached_limits || 0}
          </div>
          <div className="text-xs text-gray-500 mt-1">Breached Limits</div>
          <div className="mt-3 text-sm">
            <span className="text-yellow-600 font-medium">
              Warning: {concentrationStats?.warning_limits || 0}
            </span>
          </div>
        </div>

        {/* Compliance */}
        <div className="bg-white rounded-lg shadow p-4 border-l-4 border-green-500">
          <div className="text-sm text-gray-600">Compliance</div>
          <div className="text-2xl font-bold text-gray-900 mt-2">
            {complianceStats?.total_checks || 0}
          </div>
          <div className="text-xs text-gray-500 mt-1">Total Checks</div>
          <div className="mt-3 text-sm">
            <span className="text-green-600 font-medium">
              Compliant: {complianceStats?.checks_by_compliance_status?.compliant || 0}
            </span>
          </div>
        </div>
      </div>

      {/* Recent Alerts */}
      <div className="bg-white rounded-lg shadow">
        <div className="px-6 py-4 border-b border-gray-200">
          <h2 className="text-lg font-semibold text-gray-900">Recent Risk Alerts</h2>
        </div>
        <div className="p-6">
          {recentAlerts.length === 0 ? (
            <p className="text-gray-500 text-center py-8">No active alerts</p>
          ) : (
            <div className="space-y-3">
              {recentAlerts.map((alert) => (
                <div
                  key={alert.alert_id}
                  className="flex items-start justify-between p-4 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors"
                >
                  <div className="flex-1">
                    <div className="flex items-center gap-3">
                      <span className={`px-2 py-1 rounded-full text-xs font-medium ${getSeverityColor(alert.severity_level)}`}>
                        {alert.severity_level}
                      </span>
                      <span className="text-sm font-medium text-gray-900">{alert.alert_title}</span>
                    </div>
                    <p className="text-sm text-gray-600 mt-1">{alert.alert_description}</p>
                    <div className="flex items-center gap-4 mt-2 text-xs text-gray-500">
                      <span>Type: {alert.alert_type}</span>
                      <span>Category: {alert.risk_category}</span>
                      <span>Date: {new Date(alert.alert_date).toLocaleDateString()}</span>
                    </div>
                  </div>
                  <button
                    onClick={() => window.location.href = `/gold-lending/risk/alerts?id=${alert.alert_id}`}
                    className="ml-4 px-3 py-1 text-sm text-blue-600 hover:text-blue-800"
                  >
                    View
                  </button>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Quick Links */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <a
          href="/gold-lending/risk/credit-risk"
          className="bg-white rounded-lg shadow p-6 hover:shadow-lg transition-shadow"
        >
          <h3 className="text-lg font-semibold text-gray-900">Credit Risk</h3>
          <p className="text-sm text-gray-600 mt-2">Manage credit risk assessments and portfolio analysis</p>
          <div className="mt-4 text-blue-600 text-sm font-medium">View Details →</div>
        </a>

        <a
          href="/gold-lending/risk/operational-risk"
          className="bg-white rounded-lg shadow p-6 hover:shadow-lg transition-shadow"
        >
          <h3 className="text-lg font-semibold text-gray-900">Operational Risk</h3>
          <p className="text-sm text-gray-600 mt-2">Track operational risk events and incidents</p>
          <div className="mt-4 text-blue-600 text-sm font-medium">View Details →</div>
        </a>

        <a
          href="/gold-lending/risk/compliance"
          className="bg-white rounded-lg shadow p-6 hover:shadow-lg transition-shadow"
        >
          <h3 className="text-lg font-semibold text-gray-900">Compliance</h3>
          <p className="text-sm text-gray-600 mt-2">Monitor compliance checks and regulatory requirements</p>
          <div className="mt-4 text-blue-600 text-sm font-medium">View Details →</div>
        </a>
      </div>
    </div>
  );
}
