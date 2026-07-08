'use client';

import React, { useEffect, useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import { AlertTriangle, Search, Filter } from 'lucide-react';
import { amlService, type AMLAlert } from '@/services/aml.service';
import Link from 'next/link';
import { formatDistance } from 'date-fns';

export default function AlertsPage() {
  const [alerts, setAlerts] = useState<AMLAlert[]>([]);
  const [loading, setLoading] = useState(true);
  const [statusFilter, setStatusFilter] = useState<string>('');
  const [severityFilter, setSeverityFilter] = useState<string>('');
  const [searchTerm, setSearchTerm] = useState('');

  useEffect(() => {
    loadAlerts();
  }, [statusFilter, severityFilter]);

  const loadAlerts = async () => {
    try {
      setLoading(true);
      const params: any = {};
      if (statusFilter) params.status = statusFilter;
      if (severityFilter) params.severity = severityFilter;
      
      const data = await amlService.getAlerts(params);
      setAlerts(data);
    } catch (error) {
      console.error('Failed to load alerts:', error);
    } finally {
      setLoading(false);
    }
  };

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'critical': return 'destructive';
      case 'high': return 'destructive';
      case 'medium': return 'warning';
      case 'low': return 'secondary';
      default: return 'default';
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'open': return 'destructive';
      case 'under_review': return 'warning';
      case 'escalated': return 'destructive';
      case 'closed_false_positive': return 'secondary';
      case 'closed_reported': return 'success';
      default: return 'default';
    }
  };

  const filteredAlerts = alerts.filter(alert =>
    alert.alert_title.toLowerCase().includes(searchTerm.toLowerCase()) ||
    alert.alert_description?.toLowerCase().includes(searchTerm.toLowerCase()) ||
    alert.customer_id?.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div className="p-6 space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold">AML Alerts</h1>
          <p className="text-muted-foreground">Monitor and manage AML alerts</p>
        </div>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Filters</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid gap-4 md:grid-cols-3">
            <div className="relative">
              <Search className="absolute left-2 top-2.5 h-4 w-4 text-muted-foreground" />
              <Input
                placeholder="Search alerts..."
                className="pl-8"
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
              />
            </div>
            <Select value={statusFilter} onValueChange={setStatusFilter}>
              <SelectTrigger>
                <SelectValue placeholder="All Statuses" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="">All Statuses</SelectItem>
                <SelectItem value="open">Open</SelectItem>
                <SelectItem value="under_review">Under Review</SelectItem>
                <SelectItem value="escalated">Escalated</SelectItem>
                <SelectItem value="closed_false_positive">Closed - False Positive</SelectItem>
                <SelectItem value="closed_reported">Closed - Reported</SelectItem>
              </SelectContent>
            </Select>
            <Select value={severityFilter} onValueChange={setSeverityFilter}>
              <SelectTrigger>
                <SelectValue placeholder="All Severities" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="">All Severities</SelectItem>
                <SelectItem value="critical">Critical</SelectItem>
                <SelectItem value="high">High</SelectItem>
                <SelectItem value="medium">Medium</SelectItem>
                <SelectItem value="low">Low</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Alerts ({filteredAlerts.length})</CardTitle>
        </CardHeader>
        <CardContent>
          {loading ? (
            <div className="text-center py-8">Loading...</div>
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Alert ID</TableHead>
                  <TableHead>Title</TableHead>
                  <TableHead>Type</TableHead>
                  <TableHead>Severity</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead>Due Date</TableHead>
                  <TableHead>Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {filteredAlerts.map((alert) => (
                  <TableRow key={alert.id}>
                    <TableCell className="font-mono text-sm">
                      {alert.alert_id}
                    </TableCell>
                    <TableCell>
                      <div>
                        <div className="font-medium">{alert.alert_title}</div>
                        {alert.alert_description && (
                          <div className="text-sm text-muted-foreground truncate max-w-xs">
                            {alert.alert_description}
                          </div>
                        )}
                      </div>
                    </TableCell>
                    <TableCell>
                      <Badge variant="outline">{alert.alert_type}</Badge>
                    </TableCell>
                    <TableCell>
                      <Badge variant={getSeverityColor(alert.severity)}>
                        {alert.severity}
                      </Badge>
                    </TableCell>
                    <TableCell>
                      <Badge variant={getStatusColor(alert.status)}>
                        {alert.status.replace('_', ' ')}
                      </Badge>
                      {alert.is_overdue && (
                        <Badge variant="destructive" className="ml-2">Overdue</Badge>
                      )}
                    </TableCell>
                    <TableCell>
                      {alert.due_date ? (
                        <span className={alert.is_overdue ? 'text-red-500' : ''}>
                          {formatDistance(new Date(alert.due_date), new Date(), { addSuffix: true })}
                        </span>
                      ) : (
                        '-'
                      )}
                    </TableCell>
                    <TableCell>
                      <Link href={`/aml/alerts/${alert.id}`}>
                        <Button size="sm" variant="outline">View Details</Button>
                      </Link>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
