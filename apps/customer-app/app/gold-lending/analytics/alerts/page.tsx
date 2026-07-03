'use client';

import React, { useState, useEffect } from 'react';
import { analyticsAPI, AnalyticsAlert, AlertNotification } from '../../phase14_analytics_api';

export default function AlertsPage() {
  const [alerts, setAlerts] = useState<AnalyticsAlert[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [filterType, setFilterType] = useState<string>('');
  const [filterSeverity, setFilterSeverity] = useState<string>('');
  const [filterTriggered, setFilterTriggered] = useState<string>('');
  const [selectedAlert, setSelectedAlert] = useState<AnalyticsAlert | null>(null);
  const [notifications, setNotifications] = useState<AlertNotification[]>([]);

  useEffect(() => {
    loadAlerts();
  }, [filterType, filterSeverity, filterTriggered]);

  const loadAlerts = async () => {
    try {
      setLoading(true);
      const data = await analyticsAPI.listAnalyticsAlerts({
        alert_type: filterType || undefined,
        severity: filterSeverity || undefined,
        is_triggered: filterTriggered ? filterTriggered === 'true' : undefined,
      });
      setAlerts(data);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load alerts');
    } finally {
      setLoading(false);
    }
  };

  const handleTestAlert = async (id: string) => {
    try {
      await analyticsAPI.testAnalyticsAlert(id);
      alert('Alert test triggered successfully!');
      await loadAlerts();
    } catch (err) {
      alert('Failed to test alert: ' + (err instanceof Error ? err.message : 'Unknown error'));
    }
  };

  const loadAlertNotifications = async (alertId: string) => {
    try {
      const data = await analyticsAPI.listAlertNotifications(alertId, { limit: 10 });
      setNotifications(data);
    } catch (err) {
      console.error('Failed to load notifications:', err);
    }
  };

  const handleViewAlert = async (alert: AnalyticsAlert) => {
    setSelectedAlert(alert);
    await loadAlertNotifications(alert.id);
  };

  const getSeverityColor = (severity?: string) => {
    switch (severity) {
      case 'CRITICAL': return 'text-red-600 bg-red-100 border-red-300';
      case 'ERROR': return 'text-red-600 bg-red-100 border-red-200';
      case 'WARNING': return 'text-yellow-600 bg-yellow-100 border-yellow-300';
      case 'INFO': return 'text-blue-600 bg-blue-100 border-blue-300';
      default: return 'text-gray-600 bg-gray-100 border-gray-300';
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'ACTIVE': return 'text-green-600 bg-green-100';
      case 'INACTIVE': return 'text-gray-600 bg-gray-100';
      case 'PAUSED': return 'text-yellow-600 bg-yellow-100';
      default: return 'text-gray-600 bg-gray-100';
    }
  };

  const getDeliveryStatusColor = (status?: string) => {
    switch (status) {
      case 'DELIVERED': return 'text-green-600 bg-green-100';
      case 'SENT': return 'text-blue-600 bg-blue-100';
      case 'FAILED': return 'text-red-600 bg-red-100';
      case 'PENDING': return 'text-yellow-600 bg-yellow-100';
      default: return 'text-gray-600 bg-gray-100';
    }
  };

  if (loading && alerts.length === 0) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading alerts...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Analytics Alerts</h1>
          <p className="text-gray-600 mt-1">Monitor and manage analytics alert rules</p>
        </div>
        <button className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 flex items-center gap-2">
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
          </svg>
          Create Alert
        </button>
      </div>

      {/* Filters */}
      <div className="bg-white rounded-lg shadow p-4 border border-gray-200">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Alert Type</label>
            <select
              value={filterType}
              onChange={(e) => setFilterType(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
            >
              <option value="">All Types</option>
              <option value="THRESHOLD">Threshold</option>
              <option value="ANOMALY">Anomaly</option>
              <option value="TREND">Trend</option>
              <option value="FORECAST">Forecast</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Severity</label>
            <select
              value={filterSeverity}
              onChange={(e) => setFilterSeverity(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
            >
              <option value="">All Severities</option>
              <option value="CRITICAL">Critical</option>
              <option value="ERROR">Error</option>
              <option value="WARNING">Warning</option>
              <option value="INFO">Info</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Status</label>
            <select
              value={filterTriggered}
              onChange={(e) => setFilterTriggered(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
            >
              <option value="">All</option>
              <option value="true">Triggered</option>
              <option value="false">Not Triggered</option>
            </select>
          </div>

          <div className="flex items-end">
            <button
              onClick={loadAlerts}
              className="w-full px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200"
            >
              Apply Filters
            </button>
          </div>
        </div>
      </div>

      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <p className="text-red-600">{error}</p>
        </div>
      )}

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-white rounded-lg shadow p-4 border border-gray-200">
          <p className="text-sm text-gray-600">Total Alerts</p>
          <p className="text-2xl font-bold text-gray-900 mt-1">{alerts.length}</p>
        </div>
        <div className="bg-white rounded-lg shadow p-4 border border-gray-200">
          <p className="text-sm text-gray-600">Active</p>
          <p className="text-2xl font-bold text-green-600 mt-1">
            {alerts.filter(a => a.status === 'ACTIVE').length}
          </p>
        </div>
        <div className="bg-white rounded-lg shadow p-4 border border-gray-200">
          <p className="text-sm text-gray-600">Triggered</p>
          <p className="text-2xl font-bold text-red-600 mt-1">
            {alerts.filter(a => a.is_triggered).length}
          </p>
        </div>
        <div className="bg-white rounded-lg shadow p-4 border border-gray-200">
          <p className="text-sm text-gray-600">Critical</p>
          <p className="text-2xl font-bold text-red-600 mt-1">
            {alerts.filter(a => a.severity === 'CRITICAL').length}
          </p>
        </div>
      </div>

      {/* Alerts List */}
      <div className="space-y-4">
        {alerts.length === 0 ? (
          <div className="bg-white rounded-lg shadow border border-gray-200 p-12">
            <div className="flex flex-col items-center text-center">
              <svg className="w-16 h-16 text-gray-400 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
              </svg>
              <h3 className="text-lg font-medium text-gray-900">No alerts configured</h3>
              <p className="text-sm text-gray-500 mt-2">Create your first alert to monitor your analytics</p>
            </div>
          </div>
        ) : (
          alerts.map((alert) => (
            <div
              key={alert.id}
              className={`bg-white rounded-lg shadow border-l-4 ${getSeverityColor(alert.severity)} overflow-hidden hover:shadow-lg transition-shadow`}
            >
              <div className="p-6">
                <div className="flex items-start justify-between mb-4">
                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-2">
                      <h3 className="text-lg font-semibold text-gray-900">{alert.alert_name}</h3>
                      {alert.is_triggered && (
                        <span className="px-2 py-1 text-xs font-medium rounded-full bg-red-100 text-red-800 animate-pulse">
                          TRIGGERED
                        </span>
                      )}
                    </div>
                    <p className="text-sm text-gray-500">{alert.alert_code}</p>
                  </div>
                  <div className="flex items-center gap-2">
                    <span className={`px-3 py-1 text-xs font-medium rounded-full ${getSeverityColor(alert.severity)}`}>
                      {alert.severity}
                    </span>
                    <span className={`px-3 py-1 text-xs font-medium rounded-full ${getStatusColor(alert.status)}`}>
                      {alert.status}
                    </span>
                  </div>
                </div>

                <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
                  <div>
                    <p className="text-xs text-gray-600">Type</p>
                    <p className="text-sm font-medium text-gray-900 mt-1">{alert.alert_type}</p>
                  </div>
                  {alert.metric_name && (
                    <div>
                      <p className="text-xs text-gray-600">Metric</p>
                      <p className="text-sm font-medium text-gray-900 mt-1">{alert.metric_name}</p>
                    </div>
                  )}
                  <div>
                    <p className="text-xs text-gray-600">Evaluation Frequency</p>
                    <p className="text-sm font-medium text-gray-900 mt-1">{alert.evaluation_frequency_minutes} min</p>
                  </div>
                  <div>
                    <p className="text-xs text-gray-600">Trigger Count</p>
                    <p className="text-sm font-medium text-gray-900 mt-1">{alert.trigger_count}</p>
                  </div>
                </div>

                {/* Notification Channels */}
                {alert.notification_channels && alert.notification_channels.length > 0 && (
                  <div className="mb-4">
                    <p className="text-xs text-gray-600 mb-2">Notification Channels</p>
                    <div className="flex flex-wrap gap-2">
                      {alert.notification_channels.map((channel, idx) => (
                        <span key={idx} className="px-2 py-1 text-xs bg-blue-100 text-blue-800 rounded-full">
                          {channel}
                        </span>
                      ))}
                    </div>
                  </div>
                )}

                {/* Recipients */}
                {alert.recipients && alert.recipients.length > 0 && (
                  <div className="mb-4">
                    <p className="text-xs text-gray-600 mb-2">Recipients ({alert.recipients.length})</p>
                    <div className="flex items-center gap-2">
                      <svg className="w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                      </svg>
                      <span className="text-sm text-gray-700">
                        {alert.recipients.slice(0, 3).join(', ')}
                        {alert.recipients.length > 3 && ` +${alert.recipients.length - 3} more`}
                      </span>
                    </div>
                  </div>
                )}

                {/* Last Triggered */}
                {alert.last_triggered_at && (
                  <div className="bg-red-50 border border-red-200 rounded-lg p-3 mb-4">
                    <div className="flex items-center gap-2">
                      <svg className="w-5 h-5 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                      </svg>
                      <span className="text-sm text-red-800">
                        Last triggered: {new Date(alert.last_triggered_at).toLocaleString()}
                      </span>
                    </div>
                  </div>
                )}

                {/* Suppression */}
                {alert.suppression_enabled && alert.suppressed_until && (
                  <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-3 mb-4">
                    <div className="flex items-center gap-2">
                      <svg className="w-5 h-5 text-yellow-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M18.364 18.364A9 9 0 005.636 5.636m12.728 12.728A9 9 0 015.636 5.636m12.728 12.728L5.636 5.636" />
                      </svg>
                      <span className="text-sm text-yellow-800">
                        Suppressed until: {new Date(alert.suppressed_until).toLocaleString()}
                      </span>
                    </div>
                  </div>
                )}

                <div className="flex gap-2">
                  <button
                    onClick={() => handleTestAlert(alert.id)}
                    className="px-4 py-2 bg-blue-600 text-white text-sm rounded-lg hover:bg-blue-700 flex items-center gap-2"
                  >
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z" />
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                    Test
                  </button>
                  <button
                    onClick={() => handleViewAlert(alert)}
                    className="px-4 py-2 bg-gray-100 text-gray-700 text-sm rounded-lg hover:bg-gray-200"
                  >
                    View Details
                  </button>
                </div>
              </div>
            </div>
          ))
        )}
      </div>

      {/* Alert Details Modal */}
      {selectedAlert && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg max-w-4xl w-full max-h-[90vh] overflow-y-auto">
            <div className="p-6 border-b border-gray-200 flex justify-between items-center">
              <div>
                <h2 className="text-xl font-bold text-gray-900">{selectedAlert.alert_name}</h2>
                <p className="text-sm text-gray-500 mt-1">{selectedAlert.alert_code}</p>
              </div>
              <button
                onClick={() => setSelectedAlert(null)}
                className="text-gray-400 hover:text-gray-600"
              >
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
            
            <div className="p-6 space-y-6">
              {/* Alert Info */}
              <div>
                <h3 className="text-lg font-semibold text-gray-900 mb-3">Alert Configuration</h3>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="text-sm font-medium text-gray-700">Type</label>
                    <p className="text-sm text-gray-900 mt-1">{selectedAlert.alert_type}</p>
                  </div>
                  <div>
                    <label className="text-sm font-medium text-gray-700">Severity</label>
                    <p className="text-sm text-gray-900 mt-1">{selectedAlert.severity}</p>
                  </div>
                  <div>
                    <label className="text-sm font-medium text-gray-700">Status</label>
                    <p className="text-sm text-gray-900 mt-1">{selectedAlert.status}</p>
                  </div>
                  <div>
                    <label className="text-sm font-medium text-gray-700">Detection Algorithm</label>
                    <p className="text-sm text-gray-900 mt-1">{selectedAlert.detection_algorithm || 'N/A'}</p>
                  </div>
                  <div>
                    <label className="text-sm font-medium text-gray-700">Evaluation Frequency</label>
                    <p className="text-sm text-gray-900 mt-1">{selectedAlert.evaluation_frequency_minutes} minutes</p>
                  </div>
                  <div>
                    <label className="text-sm font-medium text-gray-700">Lookback Period</label>
                    <p className="text-sm text-gray-900 mt-1">{selectedAlert.lookback_period_minutes} minutes</p>
                  </div>
                  <div>
                    <label className="text-sm font-medium text-gray-700">Trigger Count</label>
                    <p className="text-sm text-gray-900 mt-1">{selectedAlert.trigger_count}</p>
                  </div>
                  <div>
                    <label className="text-sm font-medium text-gray-700">Currently Triggered</label>
                    <p className="text-sm text-gray-900 mt-1">{selectedAlert.is_triggered ? 'Yes' : 'No'}</p>
                  </div>
                </div>
              </div>

              {/* Recent Notifications */}
              <div>
                <h3 className="text-lg font-semibold text-gray-900 mb-3">Recent Notifications ({notifications.length})</h3>
                {notifications.length === 0 ? (
                  <p className="text-sm text-gray-500">No notifications sent yet</p>
                ) : (
                  <div className="space-y-2 max-h-60 overflow-y-auto">
                    {notifications.map((notification) => (
                      <div key={notification.id} className="border border-gray-200 rounded-lg p-3">
                        <div className="flex items-center justify-between mb-2">
                          <span className="text-sm font-medium text-gray-900">{notification.notification_code}</span>
                          <span className={`px-2 py-1 text-xs font-medium rounded-full ${getDeliveryStatusColor(notification.delivery_status)}`}>
                            {notification.delivery_status || 'PENDING'}
                          </span>
                        </div>
                        <div className="grid grid-cols-2 gap-4 text-xs text-gray-600">
                          <div>
                            <span className="font-medium">Type:</span> {notification.notification_type || 'N/A'}
                          </div>
                          <div>
                            <span className="font-medium">Recipient:</span> {notification.recipient || 'N/A'}
                          </div>
                          {notification.sent_at && (
                            <div className="col-span-2">
                              <span className="font-medium">Sent:</span> {new Date(notification.sent_at).toLocaleString()}
                            </div>
                          )}
                          {notification.acknowledged_at && (
                            <div className="col-span-2">
                              <span className="font-medium">Acknowledged:</span> {new Date(notification.acknowledged_at).toLocaleString()}
                            </div>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
