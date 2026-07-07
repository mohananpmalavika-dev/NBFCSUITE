"use client";

import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Textarea } from "@/components/ui/textarea";
import { RefreshCw, AlertTriangle, AlertCircle, Info, XCircle, CheckCircle, Bell, BellOff } from "lucide-react";
import { almService } from '@/services/almService';
import type { ALMAlertResponse } from '@/types/alm';

export default function AlertsPage() {
  const [loading, setLoading] = useState(true);
  const [alerts, setAlerts] = useState<ALMAlertResponse[]>([]);
  const [selectedAlert, setSelectedAlert] = useState<ALMAlertResponse | null>(null);
  const [showResolveDialog, setShowResolveDialog] = useState(false);
  const [showAcknowledgeDialog, setShowAcknowledgeDialog] = useState(false);
  const [resolution, setResolution] = useState('');
  const [activeTab, setActiveTab] = useState('active');

  useEffect(() => {
    fetchAlerts();
  }, []);

  const fetchAlerts = async () => {
    try {
      setLoading(true);
      const response = await almService.getAlerts();
      setAlerts(response);
    } catch (error) {
      console.error('Failed to fetch alerts:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleAcknowledge = async () => {
    if (!selectedAlert) return;
    
    try {
      await almService.acknowledgeAlert(selectedAlert.id);
      await fetchAlerts();
      setShowAcknowledgeDialog(false);
      setSelectedAlert(null);
    } catch (error) {
      console.error('Failed to acknowledge alert:', error);
    }
  };

  const handleResolve = async () => {
    if (!selectedAlert || !resolution.trim()) return;
    
    try {
      await almService.resolveAlert(selectedAlert.id, resolution);
      await fetchAlerts();
      setShowResolveDialog(false);
      setSelectedAlert(null);
      setResolution('');
    } catch (error) {
      console.error('Failed to resolve alert:', error);
    }
  };

  const getSeverityIcon = (severity: string) => {
    switch (severity) {
      case 'critical':
        return <XCircle className="h-5 w-5 text-red-600" />;
      case 'high':
        return <AlertTriangle className="h-5 w-5 text-orange-600" />;
      case 'medium':
        return <AlertCircle className="h-5 w-5 text-yellow-600" />;
      case 'low':
        return <Info className="h-5 w-5 text-blue-600" />;
      default:
        return <Bell className="h-5 w-5 text-gray-600" />;
    }
  };

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'critical':
        return 'bg-red-50 border-red-200 text-red-700';
      case 'high':
        return 'bg-orange-50 border-orange-200 text-orange-700';
      case 'medium':
        return 'bg-yellow-50 border-yellow-200 text-yellow-700';
      case 'low':
        return 'bg-blue-50 border-blue-200 text-blue-700';
      default:
        return 'bg-gray-50 border-gray-200 text-gray-700';
    }
  };

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'active':
        return <Badge variant="destructive">Active</Badge>;
      case 'acknowledged':
        return <Badge variant="default">Acknowledged</Badge>;
      case 'resolved':
        return <Badge variant="default" className="bg-green-600">Resolved</Badge>;
      default:
        return <Badge variant="secondary">{status}</Badge>;
    }
  };

  const filterAlerts = (status: string) => {
    return alerts.filter(alert => alert.status === status);
  };

  const activeAlerts = filterAlerts('active');
  const acknowledgedAlerts = filterAlerts('acknowledged');
  const resolvedAlerts = filterAlerts('resolved');

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <RefreshCw className="h-8 w-8 animate-spin text-primary" />
      </div>
    );
  }

  return (
    <div className="space-y-6 p-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">ALM Alerts</h1>
          <p className="text-muted-foreground">
            Monitor and manage ALM risk alerts and threshold breaches
          </p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" onClick={fetchAlerts}>
            <RefreshCw className="h-4 w-4 mr-2" />
            Refresh
          </Button>
        </div>
      </div>

      {/* Summary Cards */}
      <div className="grid gap-4 md:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Active Alerts</CardTitle>
            <AlertTriangle className="h-4 w-4 text-red-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-red-600">{activeAlerts.length}</div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Critical</CardTitle>
            <XCircle className="h-4 w-4 text-red-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {alerts.filter(a => a.severity === 'critical' && a.status === 'active').length}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Acknowledged</CardTitle>
            <CheckCircle className="h-4 w-4 text-blue-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{acknowledgedAlerts.length}</div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Resolved</CardTitle>
            <CheckCircle className="h-4 w-4 text-green-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{resolvedAlerts.length}</div>
          </CardContent>
        </Card>
      </div>

      {/* Alerts List */}
      <Card>
        <CardHeader>
          <CardTitle>Alert Management</CardTitle>
          <CardDescription>View and manage all ALM risk alerts</CardDescription>
        </CardHeader>
        <CardContent>
          <Tabs value={activeTab} onValueChange={setActiveTab}>
            <TabsList className="grid w-full grid-cols-3">
              <TabsTrigger value="active">
                Active ({activeAlerts.length})
              </TabsTrigger>
              <TabsTrigger value="acknowledged">
                Acknowledged ({acknowledgedAlerts.length})
              </TabsTrigger>
              <TabsTrigger value="resolved">
                Resolved ({resolvedAlerts.length})
              </TabsTrigger>
            </TabsList>

            <TabsContent value="active" className="space-y-4 mt-4">
              {activeAlerts.length === 0 ? (
                <div className="text-center py-12">
                  <CheckCircle className="h-12 w-12 mx-auto text-green-600 mb-4" />
                  <p className="text-muted-foreground">No active alerts</p>
                </div>
              ) : (
                activeAlerts.map((alert) => (
                  <AlertCard
                    key={alert.id}
                    alert={alert}
                    getSeverityIcon={getSeverityIcon}
                    getSeverityColor={getSeverityColor}
                    getStatusBadge={getStatusBadge}
                    onAcknowledge={() => {
                      setSelectedAlert(alert);
                      setShowAcknowledgeDialog(true);
                    }}
                    onResolve={() => {
                      setSelectedAlert(alert);
                      setShowResolveDialog(true);
                    }}
                  />
                ))
              )}
            </TabsContent>

            <TabsContent value="acknowledged" className="space-y-4 mt-4">
              {acknowledgedAlerts.length === 0 ? (
                <div className="text-center py-12">
                  <BellOff className="h-12 w-12 mx-auto text-muted-foreground mb-4" />
                  <p className="text-muted-foreground">No acknowledged alerts</p>
                </div>
              ) : (
                acknowledgedAlerts.map((alert) => (
                  <AlertCard
                    key={alert.id}
                    alert={alert}
                    getSeverityIcon={getSeverityIcon}
                    getSeverityColor={getSeverityColor}
                    getStatusBadge={getStatusBadge}
                    onResolve={() => {
                      setSelectedAlert(alert);
                      setShowResolveDialog(true);
                    }}
                  />
                ))
              )}
            </TabsContent>

            <TabsContent value="resolved" className="space-y-4 mt-4">
              {resolvedAlerts.length === 0 ? (
                <div className="text-center py-12">
                  <Info className="h-12 w-12 mx-auto text-muted-foreground mb-4" />
                  <p className="text-muted-foreground">No resolved alerts</p>
                </div>
              ) : (
                resolvedAlerts.map((alert) => (
                  <AlertCard
                    key={alert.id}
                    alert={alert}
                    getSeverityIcon={getSeverityIcon}
                    getSeverityColor={getSeverityColor}
                    getStatusBadge={getStatusBadge}
                  />
                ))
              )}
            </TabsContent>
          </Tabs>
        </CardContent>
      </Card>

      {/* Alert Guidelines */}
      <Card>
        <CardHeader>
          <CardTitle>Alert Response Guidelines</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <div className="border-l-4 border-red-500 pl-4 py-2">
              <h4 className="font-semibold text-red-700">Critical Alerts</h4>
              <p className="text-sm text-muted-foreground">
                Immediate action required. Escalate to senior management and treasury head.
                Implement contingency plans if thresholds are breached significantly.
              </p>
            </div>
            <div className="border-l-4 border-orange-500 pl-4 py-2">
              <h4 className="font-semibold text-orange-700">High Priority Alerts</h4>
              <p className="text-sm text-muted-foreground">
                Action required within 24 hours. Review positions and implement corrective measures.
                Monitor closely until resolved.
              </p>
            </div>
            <div className="border-l-4 border-yellow-500 pl-4 py-2">
              <h4 className="font-semibold text-yellow-700">Medium Priority Alerts</h4>
              <p className="text-sm text-muted-foreground">
                Review within 2-3 business days. Assess trend and take preventive action if deteriorating.
              </p>
            </div>
            <div className="border-l-4 border-blue-500 pl-4 py-2">
              <h4 className="font-semibold text-blue-700">Low Priority Alerts</h4>
              <p className="text-sm text-muted-foreground">
                Informational only. Monitor as part of regular ALM review process.
              </p>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Acknowledge Dialog */}
      <Dialog open={showAcknowledgeDialog} onOpenChange={setShowAcknowledgeDialog}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Acknowledge Alert</DialogTitle>
            <DialogDescription>
              Confirm that you have reviewed this alert and are taking appropriate action.
            </DialogDescription>
          </DialogHeader>
          {selectedAlert && (
            <div className="py-4">
              <div className={`p-4 border rounded-lg ${getSeverityColor(selectedAlert.severity)}`}>
                <div className="flex items-start gap-3">
                  {getSeverityIcon(selectedAlert.severity)}
                  <div className="flex-1">
                    <p className="font-semibold">{selectedAlert.alert_type}</p>
                    <p className="text-sm mt-1">{selectedAlert.message}</p>
                  </div>
                </div>
              </div>
            </div>
          )}
          <DialogFooter>
            <Button variant="outline" onClick={() => setShowAcknowledgeDialog(false)}>
              Cancel
            </Button>
            <Button onClick={handleAcknowledge}>
              Acknowledge
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Resolve Dialog */}
      <Dialog open={showResolveDialog} onOpenChange={setShowResolveDialog}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Resolve Alert</DialogTitle>
            <DialogDescription>
              Mark this alert as resolved and provide details of the resolution.
            </DialogDescription>
          </DialogHeader>
          {selectedAlert && (
            <div className="space-y-4 py-4">
              <div className={`p-4 border rounded-lg ${getSeverityColor(selectedAlert.severity)}`}>
                <div className="flex items-start gap-3">
                  {getSeverityIcon(selectedAlert.severity)}
                  <div className="flex-1">
                    <p className="font-semibold">{selectedAlert.alert_type}</p>
                    <p className="text-sm mt-1">{selectedAlert.message}</p>
                  </div>
                </div>
              </div>
              <div>
                <label className="text-sm font-medium">Resolution Details (Required)</label>
                <Textarea
                  placeholder="Describe the actions taken to resolve this alert..."
                  value={resolution}
                  onChange={(e) => setResolution(e.target.value)}
                  rows={4}
                  required
                />
              </div>
            </div>
          )}
          <DialogFooter>
            <Button variant="outline" onClick={() => setShowResolveDialog(false)}>
              Cancel
            </Button>
            <Button 
              onClick={handleResolve}
              disabled={!resolution.trim()}
              className="bg-green-600 hover:bg-green-700"
            >
              Resolve Alert
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}

function AlertCard({
  alert,
  getSeverityIcon,
  getSeverityColor,
  getStatusBadge,
  onAcknowledge,
  onResolve
}: {
  alert: ALMAlertResponse;
  getSeverityIcon: (severity: string) => React.ReactNode;
  getSeverityColor: (severity: string) => string;
  getStatusBadge: (status: string) => React.ReactNode;
  onAcknowledge?: () => void;
  onResolve?: () => void;
}) {
  return (
    <div className={`border rounded-lg p-4 ${getSeverityColor(alert.severity)}`}>
      <div className="flex items-start justify-between">
        <div className="flex items-start gap-3 flex-1">
          {getSeverityIcon(alert.severity)}
          <div className="flex-1 space-y-2">
            <div className="flex items-center gap-2">
              <h3 className="font-semibold">{alert.alert_type}</h3>
              {getStatusBadge(alert.status)}
            </div>
            
            <p className="text-sm">{alert.message}</p>
            
            <div className="grid gap-2 md:grid-cols-2 text-sm">
              <div>
                <span className="text-muted-foreground">Severity:</span>
                <span className="font-medium ml-2">{alert.severity.toUpperCase()}</span>
              </div>
              <div>
                <span className="text-muted-foreground">Triggered:</span>
                <span className="font-medium ml-2">
                  {new Date(alert.triggered_at).toLocaleString()}
                </span>
              </div>
              {alert.threshold_value && (
                <div>
                  <span className="text-muted-foreground">Threshold:</span>
                  <span className="font-medium ml-2">{alert.threshold_value}</span>
                </div>
              )}
              {alert.actual_value && (
                <div>
                  <span className="text-muted-foreground">Actual:</span>
                  <span className="font-medium ml-2">{alert.actual_value}</span>
                </div>
              )}
            </div>

            {alert.acknowledged_at && (
              <div className="text-sm">
                <span className="text-muted-foreground">Acknowledged:</span>
                <span className="ml-2">
                  {new Date(alert.acknowledged_at).toLocaleString()}
                  {alert.acknowledged_by && ` by ${alert.acknowledged_by}`}
                </span>
              </div>
            )}

            {alert.resolved_at && (
              <div className="text-sm">
                <span className="text-muted-foreground">Resolved:</span>
                <span className="ml-2">
                  {new Date(alert.resolved_at).toLocaleString()}
                  {alert.resolved_by && ` by ${alert.resolved_by}`}
                </span>
              </div>
            )}

            {alert.resolution && (
              <div className="mt-2 p-3 bg-white/50 rounded border">
                <p className="text-sm font-medium mb-1">Resolution:</p>
                <p className="text-sm">{alert.resolution}</p>
              </div>
            )}
          </div>
        </div>

        <div className="flex gap-2 ml-4">
          {alert.status === 'active' && onAcknowledge && (
            <Button variant="outline" size="sm" onClick={onAcknowledge}>
              <CheckCircle className="h-4 w-4 mr-1" />
              Acknowledge
            </Button>
          )}
          {(alert.status === 'active' || alert.status === 'acknowledged') && onResolve && (
            <Button variant="default" size="sm" onClick={onResolve} className="bg-green-600 hover:bg-green-700">
              <CheckCircle className="h-4 w-4 mr-1" />
              Resolve
            </Button>
          )}
        </div>
      </div>
    </div>
  );
}
