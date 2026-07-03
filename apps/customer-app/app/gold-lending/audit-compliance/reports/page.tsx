'use client';

import { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { FileText, Download, Send, Plus, AlertCircle } from 'lucide-react';

export default function RegulatoryReportsPage() {
  const [reports, setReports] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadReports();
  }, []);

  const loadReports = async () => {
    setLoading(true);
    try {
      const response = await fetch('/api/v1/gold/audit-compliance/regulatory-reports');
      if (response.ok) {
        setReports(await response.json());
      }
    } catch (error) {
      console.error('Error loading reports:', error);
    } finally {
      setLoading(false);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status?.toLowerCase()) {
      case 'submitted': return 'default';
      case 'approved': return 'default';
      case 'draft': return 'secondary';
      case 'overdue': return 'destructive';
      default: return 'outline';
    }
  };

  return (
    <div className="container mx-auto p-6 space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold">Regulatory Reports</h1>
          <p className="text-muted-foreground">Manage compliance reporting to regulatory bodies</p>
        </div>
        <Button>
          <Plus className="mr-2 h-4 w-4" />
          New Report
        </Button>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Regulatory Reports</CardTitle>
          <CardDescription>Track submissions to regulatory authorities</CardDescription>
        </CardHeader>
        <CardContent>
          {loading ? (
            <div className="text-center py-8">Loading...</div>
          ) : reports.length === 0 ? (
            <div className="text-center py-8 text-muted-foreground">No reports found</div>
          ) : (
            <div className="space-y-4">
              {reports.map((report) => (
                <div key={report.report_id} className="border rounded-lg p-4 hover:bg-muted/50 transition-colors">
                  <div className="flex justify-between items-start mb-3">
                    <div>
                      <h3 className="font-semibold">{report.report_name}</h3>
                      <p className="text-sm text-muted-foreground">{report.report_type}</p>
                    </div>
                    <div className="flex gap-2">
                      {report.is_overdue && (
                        <Badge variant="destructive">
                          <AlertCircle className="h-3 w-3 mr-1" />
                          Overdue
                        </Badge>
                      )}
                      <Badge variant={getStatusColor(report.report_status)}>
                        {report.report_status}
                      </Badge>
                    </div>
                  </div>

                  <div className="grid grid-cols-2 gap-4 text-sm mb-3">
                    <div>
                      <span className="text-muted-foreground">Regulatory Body:</span>
                      <p className="font-medium">{report.regulatory_body}</p>
                    </div>
                    <div>
                      <span className="text-muted-foreground">Reporting Period:</span>
                      <p className="font-medium">
                        {new Date(report.reporting_period_start).toLocaleDateString()} - 
                        {new Date(report.reporting_period_end).toLocaleDateString()}
                      </p>
                    </div>
                    <div>
                      <span className="text-muted-foreground">Due Date:</span>
                      <p className="font-medium">{new Date(report.due_date).toLocaleDateString()}</p>
                    </div>
                    {report.submission_date && (
                      <div>
                        <span className="text-muted-foreground">Submitted:</span>
                        <p className="font-medium">{new Date(report.submission_date).toLocaleDateString()}</p>
                      </div>
                    )}
                  </div>

                  <div className="flex gap-2">
                    <Button size="sm" variant="outline">
                      <FileText className="h-4 w-4 mr-2" />
                      View
                    </Button>
                    {report.report_status === 'draft' && (
                      <Button size="sm" variant="outline">
                        <Send className="h-4 w-4 mr-2" />
                        Submit
                      </Button>
                    )}
                    {report.report_status === 'submitted' && (
                      <Button size="sm" variant="outline">
                        <Download className="h-4 w-4 mr-2" />
                        Download
                      </Button>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
