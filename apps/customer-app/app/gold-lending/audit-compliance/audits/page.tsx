'use client';

import { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Calendar, CheckCircle, Clock, FileText, Plus } from 'lucide-react';

export default function AuditsPage() {
  const [schedules, setSchedules] = useState<any[]>([]);
  const [executions, setExecutions] = useState<any[]>([]);
  const [findings, setFindings] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    setLoading(true);
    try {
      const [schedulesRes, executionsRes, findingsRes] = await Promise.all([
        fetch('/api/v1/gold/audit-compliance/audit-schedules'),
        fetch('/api/v1/gold/audit-compliance/audit-executions'),
        fetch('/api/v1/gold/audit-compliance/audit-findings'),
      ]);

      if (schedulesRes.ok) setSchedules(await schedulesRes.json());
      if (executionsRes.ok) setExecutions(await executionsRes.json());
      if (findingsRes.ok) setFindings(await findingsRes.json());
    } catch (error) {
      console.error('Error loading audit data:', error);
    } finally {
      setLoading(false);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status?.toLowerCase()) {
      case 'completed': return 'default';
      case 'in_progress': return 'default';
      case 'scheduled': return 'secondary';
      case 'overdue': return 'destructive';
      default: return 'outline';
    }
  };

  return (
    <div className="container mx-auto p-6 space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold">Audit Management</h1>
          <p className="text-muted-foreground">Schedule and execute audits</p>
        </div>
        <Button>
          <Plus className="mr-2 h-4 w-4" />
          Schedule Audit
        </Button>
      </div>

      <Tabs defaultValue="executions">
        <TabsList>
          <TabsTrigger value="executions">Audit Executions</TabsTrigger>
          <TabsTrigger value="schedules">Schedules</TabsTrigger>
          <TabsTrigger value="findings">Findings</TabsTrigger>
        </TabsList>

        <TabsContent value="executions" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Audit Executions</CardTitle>
              <CardDescription>Track ongoing and completed audits</CardDescription>
            </CardHeader>
            <CardContent>
              {loading ? (
                <div className="text-center py-8">Loading...</div>
              ) : (
                <div className="space-y-4">
                  {executions.map((execution) => (
                    <div key={execution.execution_id} className="border rounded-lg p-4">
                      <div className="flex justify-between items-start mb-2">
                        <div>
                          <h3 className="font-semibold">{execution.audit_name}</h3>
                          <p className="text-sm text-muted-foreground">{execution.audit_type}</p>
                        </div>
                        <Badge variant={getStatusColor(execution.execution_status)}>
                          {execution.execution_status}
                        </Badge>
                      </div>
                      <p className="text-sm mb-3">{execution.audit_scope}</p>
                      <div className="grid grid-cols-2 gap-4 text-sm">
                        <div className="flex items-center gap-2">
                          <Calendar className="h-4 w-4 text-muted-foreground" />
                          <span>Start: {new Date(execution.planned_start_date).toLocaleDateString()}</span>
                        </div>
                        <div className="flex items-center gap-2">
                          <Clock className="h-4 w-4 text-muted-foreground" />
                          <span>Progress: {execution.completion_percentage}%</span>
                        </div>
                      </div>
                      {execution.overall_rating && (
                        <div className="mt-2">
                          <Badge variant="outline">Rating: {execution.overall_rating}</Badge>
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="schedules" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Audit Schedules</CardTitle>
              <CardDescription>Recurring audit configurations</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {schedules.map((schedule) => (
                  <div key={schedule.schedule_id} className="border rounded-lg p-4">
                    <div className="flex justify-between items-start mb-2">
                      <div>
                        <h3 className="font-semibold">{schedule.schedule_code}</h3>
                        <p className="text-sm text-muted-foreground">{schedule.audit_type}</p>
                      </div>
                      <Badge variant={getStatusColor(schedule.schedule_status)}>
                        {schedule.schedule_status}
                      </Badge>
                    </div>
                    <div className="grid grid-cols-2 gap-4 text-sm text-muted-foreground">
                      <span>Frequency: {schedule.frequency}</span>
                      <span>Next: {new Date(schedule.next_audit_date).toLocaleDateString()}</span>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="findings" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Audit Findings</CardTitle>
              <CardDescription>Issues discovered during audits</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {findings.map((finding) => (
                  <div key={finding.finding_id} className="border rounded-lg p-4">
                    <div className="flex justify-between items-start mb-2">
                      <div className="flex gap-2">
                        <Badge variant={finding.severity_level === 'critical' ? 'destructive' : 'default'}>
                          {finding.severity_level}
                        </Badge>
                        <Badge variant="outline">{finding.finding_type}</Badge>
                      </div>
                      <Badge variant={finding.finding_status === 'verified' ? 'default' : 'secondary'}>
                        {finding.finding_status}
                      </Badge>
                    </div>
                    <h3 className="font-semibold mb-1">{finding.finding_title}</h3>
                    <p className="text-sm text-muted-foreground mb-2">{finding.finding_description}</p>
                    {finding.recommendation && (
                      <div className="mt-2 p-2 bg-muted rounded text-sm">
                        <strong>Recommendation:</strong> {finding.recommendation}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}
