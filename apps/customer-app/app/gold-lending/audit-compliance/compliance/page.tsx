'use client';

import { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { AlertTriangle, Plus, Search, FileText } from 'lucide-react';

export default function CompliancePage() {
  const [rules, setRules] = useState<any[]>([]);
  const [violations, setViolations] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('violations');
  const [filters, setFilters] = useState({ status: 'all', severity: 'all' });

  useEffect(() => {
    loadData();
  }, [filters]);

  const loadData = async () => {
    setLoading(true);
    try {
      const [rulesRes, violationsRes] = await Promise.all([
        fetch('/api/v1/gold/audit-compliance/compliance-rules'),
        fetch(`/api/v1/gold/audit-compliance/compliance-violations?${new URLSearchParams({
          ...(filters.status !== 'all' && { violation_status: filters.status }),
          ...(filters.severity !== 'all' && { severity_level: filters.severity }),
        })}`),
      ]);

      if (rulesRes.ok) setRules(await rulesRes.json());
      if (violationsRes.ok) setViolations(await violationsRes.json());
    } catch (error) {
      console.error('Error loading compliance data:', error);
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

  return (
    <div className="container mx-auto p-6 space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold">Compliance Management</h1>
          <p className="text-muted-foreground">Manage compliance rules and violations</p>
        </div>
        <Button>
          <Plus className="mr-2 h-4 w-4" />
          New Rule
        </Button>
      </div>

      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList>
          <TabsTrigger value="violations">Violations</TabsTrigger>
          <TabsTrigger value="rules">Compliance Rules</TabsTrigger>
        </TabsList>

        <TabsContent value="violations" className="space-y-4">
          <Card>
            <CardHeader>
              <div className="flex justify-between items-center">
                <div>
                  <CardTitle>Compliance Violations</CardTitle>
                  <CardDescription>Track and manage compliance violations</CardDescription>
                </div>
                <div className="flex gap-2">
                  <Select value={filters.status} onValueChange={(v) => setFilters({ ...filters, status: v })}>
                    <SelectTrigger className="w-[150px]">
                      <SelectValue placeholder="Status" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="all">All Status</SelectItem>
                      <SelectItem value="open">Open</SelectItem>
                      <SelectItem value="in_progress">In Progress</SelectItem>
                      <SelectItem value="closed">Closed</SelectItem>
                    </SelectContent>
                  </Select>
                  <Select value={filters.severity} onValueChange={(v) => setFilters({ ...filters, severity: v })}>
                    <SelectTrigger className="w-[150px]">
                      <SelectValue placeholder="Severity" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="all">All Severity</SelectItem>
                      <SelectItem value="critical">Critical</SelectItem>
                      <SelectItem value="high">High</SelectItem>
                      <SelectItem value="medium">Medium</SelectItem>
                      <SelectItem value="low">Low</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>
            </CardHeader>
            <CardContent>
              {loading ? (
                <div className="text-center py-8">Loading...</div>
              ) : violations.length === 0 ? (
                <div className="text-center py-8 text-muted-foreground">No violations found</div>
              ) : (
                <div className="space-y-4">
                  {violations.map((violation) => (
                    <div key={violation.violation_id} className="border rounded-lg p-4 hover:bg-muted/50 transition-colors">
                      <div className="flex justify-between items-start mb-2">
                        <div className="flex gap-2">
                          <Badge variant={getSeverityColor(violation.severity_level)}>
                            {violation.severity_level}
                          </Badge>
                          <Badge variant="outline">{violation.violation_type}</Badge>
                        </div>
                        <Badge variant={violation.violation_status === 'closed' ? 'secondary' : 'default'}>
                          {violation.violation_status}
                        </Badge>
                      </div>
                      <h3 className="font-semibold mb-1">{violation.violation_description}</h3>
                      <p className="text-sm text-muted-foreground mb-2">
                        Entity: {violation.entity_type} - {violation.entity_id}
                      </p>
                      <div className="flex justify-between items-center text-xs text-muted-foreground">
                        <span>Detected: {new Date(violation.violation_date).toLocaleDateString()}</span>
                        {violation.financial_impact && (
                          <span className="font-medium">Impact: ${violation.financial_impact.toLocaleString()}</span>
                        )}
                      </div>
                      {violation.requires_regulatory_reporting && (
                        <div className="mt-2">
                          <Badge variant="destructive" className="text-xs">
                            <AlertTriangle className="h-3 w-3 mr-1" />
                            Regulatory Reporting Required
                          </Badge>
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="rules" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Compliance Rules</CardTitle>
              <CardDescription>Configure compliance monitoring rules</CardDescription>
            </CardHeader>
            <CardContent>
              {loading ? (
                <div className="text-center py-8">Loading...</div>
              ) : (
                <div className="space-y-4">
                  {rules.map((rule) => (
                    <div key={rule.rule_id} className="border rounded-lg p-4">
                      <div className="flex justify-between items-start mb-2">
                        <div>
                          <h3 className="font-semibold">{rule.rule_code}</h3>
                          <p className="text-sm text-muted-foreground">{rule.rule_name}</p>
                        </div>
                        <div className="flex gap-2">
                          <Badge variant={rule.is_active ? 'default' : 'secondary'}>
                            {rule.is_active ? 'Active' : 'Inactive'}
                          </Badge>
                          <Badge variant={getSeverityColor(rule.severity_level)}>
                            {rule.severity_level}
                          </Badge>
                        </div>
                      </div>
                      <p className="text-sm mb-2">{rule.rule_description}</p>
                      <div className="flex gap-4 text-xs text-muted-foreground">
                        <span>Category: {rule.rule_category}</span>
                        <span>Type: {rule.rule_type}</span>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}
