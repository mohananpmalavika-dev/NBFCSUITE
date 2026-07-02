'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/app/components/eds/card';
import { Button } from '@/app/components/eds/button';
import { Badge } from '@/app/components/eds/badge';
import {
  ClipboardCheck,
  Calendar,
  AlertTriangle,
  CheckCircle,
  Clock,
  Plus,
  Search,
  Filter,
  FileText,
  User,
} from 'lucide-react';
import { goldApi } from '../../goldApi';

interface VaultAudit {
  id: string;
  vault_id: string;
  vault_name: string;
  audit_type: string;
  scheduled_date: string;
  started_at?: string;
  completed_at?: string;
  status: string;
  auditor_id: string;
  auditor_name?: string;
  findings_count: number;
  discrepancies_count: number;
  notes?: string;
}

interface AuditFinding {
  id: string;
  audit_id: string;
  finding_type: string;
  severity: string;
  description: string;
  location: string;
  expected_value?: string;
  actual_value?: string;
  action_taken?: string;
  resolved: boolean;
}

export default function VaultAuditsPage() {
  const router = useRouter();
  const [audits, setAudits] = useState<VaultAudit[]>([]);
  const [findings, setFindings] = useState<AuditFinding[]>([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState('all');
  const [searchTerm, setSearchTerm] = useState('');

  useEffect(() => {
    loadAudits();
  }, []);

  const loadAudits = async () => {
    try {
      setLoading(true);
      const data = await goldApi.getVaultAudits();
      setAudits(data);
    } catch (error) {
      console.error('Failed to load audits:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleScheduleAudit = async () => {
    const vaultId = prompt('Enter Vault ID:');
    if (!vaultId) return;

    const auditType = prompt('Enter audit type (routine/surprise/compliance/incident):');
    if (!auditType) return;

    const scheduledDate = prompt('Enter scheduled date (YYYY-MM-DD):');
    if (!scheduledDate) return;

    try {
      await goldApi.createVaultAudit({
        vault_id: vaultId,
        audit_type: auditType,
        scheduled_date: scheduledDate,
        auditor_id: 'current-user-id', // Replace with actual user ID
        notes: 'Scheduled via web interface',
      });
      await loadAudits();
      alert('Audit scheduled successfully');
    } catch (error) {
      console.error('Failed to schedule audit:', error);
      alert('Failed to schedule audit');
    }
  };

  const handleStartAudit = async (auditId: string) => {
    if (!confirm('Start this audit now?')) return;

    try {
      // Update audit status to in_progress
      // This would be a PATCH endpoint in the real implementation
      alert('Audit started - full implementation requires additional API endpoint');
      await loadAudits();
    } catch (error) {
      console.error('Failed to start audit:', error);
      alert('Failed to start audit');
    }
  };

  const handleCompleteAudit = async (auditId: string) => {
    if (!confirm('Mark this audit as complete?')) return;

    try {
      // Update audit status to completed
      // This would be a PATCH endpoint in the real implementation
      alert('Audit completed - full implementation requires additional API endpoint');
      await loadAudits();
    } catch (error) {
      console.error('Failed to complete audit:', error);
      alert('Failed to complete audit');
    }
  };

  const handleViewFindings = async (auditId: string) => {
    try {
      const findingsData = await goldApi.getAuditFindings(auditId);
      setFindings(findingsData);
    } catch (error) {
      console.error('Failed to load findings:', error);
    }
  };

  const getStatusColor = (status: string) => {
    const colors: Record<string, string> = {
      scheduled: 'bg-blue-100 text-blue-800',
      in_progress: 'bg-yellow-100 text-yellow-800',
      completed: 'bg-green-100 text-green-800',
      cancelled: 'bg-gray-100 text-gray-800',
    };
    return colors[status] || 'bg-gray-100 text-gray-800';
  };

  const getSeverityColor = (severity: string) => {
    const colors: Record<string, string> = {
      critical: 'bg-red-100 text-red-800',
      high: 'bg-orange-100 text-orange-800',
      medium: 'bg-yellow-100 text-yellow-800',
      low: 'bg-blue-100 text-blue-800',
      info: 'bg-gray-100 text-gray-800',
    };
    return colors[severity] || 'bg-gray-100 text-gray-800';
  };

  const filteredAudits = audits.filter((audit) => {
    if (filter !== 'all' && audit.status !== filter) return false;
    if (searchTerm && !audit.vault_name?.toLowerCase().includes(searchTerm.toLowerCase())) return false;
    return true;
  });

  const stats = {
    total: audits.length,
    scheduled: audits.filter((a) => a.status === 'scheduled').length,
    in_progress: audits.filter((a) => a.status === 'in_progress').length,
    completed: audits.filter((a) => a.status === 'completed').length,
    total_findings: audits.reduce((sum, a) => sum + a.findings_count, 0),
    total_discrepancies: audits.reduce((sum, a) => sum + a.discrepancies_count, 0),
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <ClipboardCheck className="h-12 w-12 animate-spin mx-auto text-gray-400" />
          <p className="mt-4 text-gray-600">Loading audits...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold flex items-center gap-2">
            <ClipboardCheck className="h-8 w-8" />
            Vault Audits
          </h1>
          <p className="text-gray-600 mt-1">Schedule and manage vault audit activities</p>
        </div>
        <Button onClick={handleScheduleAudit}>
          <Plus className="h-4 w-4 mr-2" />
          Schedule Audit
        </Button>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-6 gap-4">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-gray-600">Total Audits</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.total}</div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-gray-600">Scheduled</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-blue-600">{stats.scheduled}</div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-gray-600">In Progress</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-yellow-600">{stats.in_progress}</div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-gray-600">Completed</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-green-600">{stats.completed}</div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-gray-600">Total Findings</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-orange-600">{stats.total_findings}</div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-gray-600">Discrepancies</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-red-600">{stats.total_discrepancies}</div>
          </CardContent>
        </Card>
      </div>

      {/* Filters */}
      <Card>
        <CardContent className="pt-6">
          <div className="flex gap-4 items-center">
            <div className="flex-1 relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
              <input
                type="text"
                placeholder="Search by vault name..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full pl-10 pr-4 py-2 border rounded-lg"
              />
            </div>
            <div className="flex gap-2">
              <Button
                variant={filter === 'all' ? 'default' : 'outline'}
                onClick={() => setFilter('all')}
              >
                All
              </Button>
              <Button
                variant={filter === 'scheduled' ? 'default' : 'outline'}
                onClick={() => setFilter('scheduled')}
              >
                Scheduled
              </Button>
              <Button
                variant={filter === 'in_progress' ? 'default' : 'outline'}
                onClick={() => setFilter('in_progress')}
              >
                In Progress
              </Button>
              <Button
                variant={filter === 'completed' ? 'default' : 'outline'}
                onClick={() => setFilter('completed')}
              >
                Completed
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Audits List */}
      <div className="grid grid-cols-1 gap-4">
        {filteredAudits.map((audit) => (
          <Card key={audit.id}>
            <CardContent className="pt-6">
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-2">
                    <h3 className="text-lg font-semibold">{audit.vault_name || audit.vault_id}</h3>
                    <Badge className={getStatusColor(audit.status)}>
                      {audit.status.replace('_', ' ').toUpperCase()}
                    </Badge>
                    <Badge variant="outline">{audit.audit_type}</Badge>
                  </div>

                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                    <div>
                      <span className="text-gray-600">Scheduled:</span>
                      <p className="font-medium flex items-center gap-1">
                        <Calendar className="h-3 w-3" />
                        {new Date(audit.scheduled_date).toLocaleDateString()}
                      </p>
                    </div>

                    {audit.started_at && (
                      <div>
                        <span className="text-gray-600">Started:</span>
                        <p className="font-medium">
                          {new Date(audit.started_at).toLocaleString()}
                        </p>
                      </div>
                    )}

                    {audit.completed_at && (
                      <div>
                        <span className="text-gray-600">Completed:</span>
                        <p className="font-medium">
                          {new Date(audit.completed_at).toLocaleString()}
                        </p>
                      </div>
                    )}

                    <div>
                      <span className="text-gray-600">Auditor:</span>
                      <p className="font-medium flex items-center gap-1">
                        <User className="h-3 w-3" />
                        {audit.auditor_name || audit.auditor_id}
                      </p>
                    </div>

                    <div>
                      <span className="text-gray-600">Findings:</span>
                      <p className="font-medium flex items-center gap-1">
                        <FileText className="h-3 w-3" />
                        {audit.findings_count}
                      </p>
                    </div>

                    {audit.discrepancies_count > 0 && (
                      <div>
                        <span className="text-gray-600">Discrepancies:</span>
                        <p className="font-medium text-red-600 flex items-center gap-1">
                          <AlertTriangle className="h-3 w-3" />
                          {audit.discrepancies_count}
                        </p>
                      </div>
                    )}
                  </div>

                  {audit.notes && (
                    <p className="mt-2 text-sm text-gray-600 italic">{audit.notes}</p>
                  )}
                </div>

                <div className="flex flex-col gap-2 ml-4">
                  {audit.status === 'scheduled' && (
                    <Button size="sm" onClick={() => handleStartAudit(audit.id)}>
                      <Clock className="h-3 w-3 mr-1" />
                      Start
                    </Button>
                  )}
                  {audit.status === 'in_progress' && (
                    <Button size="sm" onClick={() => handleCompleteAudit(audit.id)}>
                      <CheckCircle className="h-3 w-3 mr-1" />
                      Complete
                    </Button>
                  )}
                  <Button
                    size="sm"
                    variant="outline"
                    onClick={() => handleViewFindings(audit.id)}
                  >
                    <FileText className="h-3 w-3 mr-1" />
                    Findings
                  </Button>
                  <Button
                    size="sm"
                    variant="outline"
                    onClick={() => router.push(`/gold-lending/vault/${audit.vault_id}`)}
                  >
                    View Vault
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {filteredAudits.length === 0 && (
        <Card>
          <CardContent className="py-12 text-center">
            <ClipboardCheck className="h-12 w-12 mx-auto text-gray-400 mb-4" />
            <p className="text-gray-600">No audits found</p>
            <Button onClick={handleScheduleAudit} className="mt-4">
              Schedule First Audit
            </Button>
          </CardContent>
        </Card>
      )}

      {/* Findings Panel */}
      {findings.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>Audit Findings</CardTitle>
            <CardDescription>{findings.length} findings for selected audit</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {findings.map((finding) => (
                <div
                  key={finding.id}
                  className="border-l-4 border-orange-500 pl-4 py-2 bg-gray-50 rounded"
                >
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-1">
                        <Badge className={getSeverityColor(finding.severity)}>
                          {finding.severity.toUpperCase()}
                        </Badge>
                        <Badge variant="outline">{finding.finding_type.replace('_', ' ')}</Badge>
                        {finding.resolved && (
                          <Badge className="bg-green-100 text-green-800">
                            <CheckCircle className="h-3 w-3 mr-1" />
                            Resolved
                          </Badge>
                        )}
                      </div>
                      <p className="font-semibold">{finding.description}</p>
                      <p className="text-sm text-gray-600 mt-1">Location: {finding.location}</p>
                      {finding.expected_value && finding.actual_value && (
                        <div className="text-sm mt-2">
                          <span className="text-gray-600">Expected: </span>
                          <span className="font-medium">{finding.expected_value}</span>
                          <span className="text-gray-600 mx-2">|</span>
                          <span className="text-gray-600">Actual: </span>
                          <span className="font-medium text-red-600">{finding.actual_value}</span>
                        </div>
                      )}
                      {finding.action_taken && (
                        <p className="text-sm text-green-600 mt-2">
                          Action: {finding.action_taken}
                        </p>
                      )}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
