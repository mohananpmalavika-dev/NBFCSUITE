'use client';

import { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { 
  ShieldCheck, AlertTriangle, FileText, Calendar, 
  TrendingUp, Activity, CheckCircle, XCircle 
} from 'lucide-react';

export default function AuditComplianceDashboard() {
  const [auditStats, setAuditStats] = useState<any>(null);
  const [complianceStats, setComplianceStats] = useState<any>(null);
  const [recentAudits, setRecentAudits] = useState<any[]>([]);
  const [recentViolations, setRecentViolations] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    setLoading(true);
    try {
      // Load statistics
      const [auditStatsRes, complianceStatsRes] = await Promise.all([
        fetch('/api/v1/gold/audit-compliance/statistics/audit-trails'),
        fetch('/api/v1/gold/audit-compliance/statistics/compliance'),
      ]);

      if (auditStatsRes.ok) setAuditStats(await auditStatsRes.json());
      if (complianceStatsRes.ok) setComplianceStats(await complianceStatsRes.json());

      // Load recent data
      const [auditsRes, violationsRes] = await Promise.all([
        fetch('/api/v1/gold/audit-compliance/audit-trails?limit=10'),
        fetch('/api/v1/gold/audit-compliance/compliance-violations?limit=10'),
      ]);

      if (auditsRes.ok) setRecentAudits(await auditsRes.json());
      if (violationsRes.ok) setRecentViolations(await violationsRes.json());
    } catch (error) {
      console.error('Error loading dashboard:', error);
    } finally {
      setLoading(false);
    }
  };

  const getSeverityColor = (severity: string) => {
    switch (severity?.toLowerCase()) {
      case 'critical': return 'destructive';
      case 'high': return 'destructive';
      case 'medium': return 'default';
      case 'low': return 'secondary';
      default: return 'outline';
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
      </div>
    );
  }

  return (
    <div className="container mx-auto p-6 space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold">Audit & Compliance Dashboard</h1>
          <p className="text-muted-foreground">Monitor audit trails, compliance, and regulatory reporting</p>
        </div>
      </div>

      {/* Key Metrics */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Audit Events</CardTitle>
            <Activity className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{auditStats?.total_events || 0}</div>
            <p className="text-xs text-muted-foreground">
              {auditStats?.security_events || 0} security events
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Compliance Rules</CardTitle>
            <ShieldCheck className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{complianceStats?.total_rules || 0}</div>
            <p className="text-xs text-muted-foreground">
              {complianceStats?.active_rules || 0} active
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Open Violations</CardTitle>
            <AlertTriangle className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{complianceStats?.open_violations || 0}</div>
            <p className="text-xs text-muted-foreground">
              of {complianceStats?.total_violations || 0} total
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Financial Impact</CardTitle>
            <TrendingUp className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              ${(complianceStats?.total_financial_impact || 0).toLocaleString()}
            </div>
            <p className="text-xs text-muted-foreground">Total exposure</p>
          </CardContent>
        </Card>
      </div>

      {/* Main Content Tabs */}
      <Tabs defaultValue="audit-trails" className="space-y-4">
        <TabsList>
          <TabsTrigger value="audit-trails">Audit Trails</TabsTrigger>
          <TabsTrigger value="violations">Compliance Violations</TabsTrigger>
          <TabsTrigger value="analytics">Analytics</TabsTrigger>
        </TabsList>

        <TabsContent value="audit-trails" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Recent Audit Events</CardTitle>
              <CardDescription>Latest system audit trail entries</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {recentAudits.length === 0 ? (
                  <p className="text-muted-foreground text-center py-4">No audit trails found</p>
                ) : (
                  recentAudits.map((audit) => (
                    <div key={audit.audit_id} className="flex items-center justify-between border-b pb-3">
                      <div className="space-y-1">
                        <div className="flex items-center gap-2">
                          <Badge variant={audit.security_flag ? 'destructive' : 'default'}>
                            {audit.event_type}
                          </Badge>
                          <span className="text-sm font-medium">{audit.event_category}</span>
                        </div>
                        <p className="text-sm text-muted-foreground">
                          {audit.entity_type}: {audit.entity_id}
                        </p>
                        <p className="text-xs text-muted-foreground">
                          {new Date(audit.event_timestamp).toLocaleString()}
                        </p>
                      </div>
                      <div className="flex items-center gap-2">
                        {audit.security_flag && <Badge variant="destructive">Security</Badge>}
                        {audit.compliance_flag && <Badge>Compliance</Badge>}
                        {audit.fraud_flag && <Badge variant="destructive">Fraud</Badge>}
                      </div>
                    </div>
                  ))
                )}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="violations" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Recent Compliance Violations</CardTitle>
              <CardDescription>Latest compliance rule violations</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {recentViolations.length === 0 ? (
                  <div className="text-center py-8">
                    <CheckCircle className="h-12 w-12 text-green-500 mx-auto mb-2" />
                    <p className="text-muted-foreground">No violations found</p>
                  </div>
                ) : (
                  recentViolations.map((violation) => (
                    <div key={violation.violation_id} className="flex items-start justify-between border-b pb-3">
                      <div className="space-y-1 flex-1">
                        <div className="flex items-center gap-2">
                          <Badge variant={getSeverityColor(violation.severity_level)}>
                            {violation.severity_level}
                          </Badge>
                          <span className="text-sm font-medium">{violation.violation_type}</span>
                        </div>
                        <p className="text-sm">{violation.violation_description}</p>
                        <p className="text-xs text-muted-foreground">
                          {new Date(violation.violation_date).toLocaleString()}
                        </p>
                      </div>
                      <Badge variant={violation.violation_status === 'closed' ? 'secondary' : 'default'}>
                        {violation.violation_status}
                      </Badge>
                    </div>
                  ))
                )}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="analytics" className="space-y-4">
          <div className="grid gap-4 md:grid-cols-2">
            <Card>
              <CardHeader>
                <CardTitle>Events by Category</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  {auditStats?.events_by_category && Object.entries(auditStats.events_by_category).map(([category, count]: any) => (
                    <div key={category} className="flex justify-between items-center">
                      <span className="text-sm">{category}</span>
                      <Badge variant="outline">{count}</Badge>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Violations by Severity</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  {complianceStats?.violations_by_severity && Object.entries(complianceStats.violations_by_severity).map(([severity, count]: any) => (
                    <div key={severity} className="flex justify-between items-center">
                      <span className="text-sm">{severity}</span>
                      <Badge variant={getSeverityColor(severity)}>{count}</Badge>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>
      </Tabs>
    </div>
  );
}
